import logging
import asyncio
from src.services.balena_service import BalenaService
from src.repositories.fleet_vars_repo import FleetVarsRepository
from src.repositories.device_vars_repo import DeviceVarsRepository

logger = logging.getLogger(__name__)

class ConfigurationSyncService:
    
    MAX_CONCURRENT_TASKS = 5

    @classmethod
    async def sync_all_variables(cls):
        """
        Proceso MAESTRO:
        1. Trae y guarda variables de TODAS las flotas.
        2. Itera equipos y trae sus variables en paralelo.
        """
        logger.info(f"🔧 INICIANDO SINCRONIZACIÓN DE CONFIGURACIÓN (Max {cls.MAX_CONCURRENT_TASKS} hilos)...")
        
        if not BalenaService.login():
            logger.error("🛑 Abortado: Fallo login Balena.")
            return False

        # --- FASE 1: VARIABLES DE FLOTAS ---
        # Obtenemos la lista de flotas primero
        raw_fleets = BalenaService.get_fleets()
        
        all_fleet_vars = []
        slug_to_name_map = {} # Mapa Slug (admin/andina_1) -> Nombre Real (Andina_1)

        for f in raw_fleets:
            app_name = f.get("app_name") # Ej: Andina_1
            slug = f.get("slug")         # Ej: admin/andina_1
            
            if not app_name or not slug: continue
            
            # Guardamos la relación para usarla en la Fase 2
            slug_to_name_map[slug] = app_name

            # API Balena requiere el SLUG
            vars_list = BalenaService.get_fleet_vars(slug)
            
            for v in vars_list:
                all_fleet_vars.append({
                    "fleet_slug": app_name, # <--- GUARDAMOS EL NOMBRE REAL EN BD
                    "name": v.get("name"),
                    "value": v.get("value")
                })
        
        if all_fleet_vars:
            await FleetVarsRepository.upsert_batch(all_fleet_vars)
            logger.info(f"✅ Guardadas {len(all_fleet_vars)} variables de flotas.")

        # --- FASE 2: VARIABLES DE DISPOSITIVOS (PARALELO) ---
        total_vars_processed = 0
        semaphore = asyncio.Semaphore(cls.MAX_CONCURRENT_TASKS)

        # CORRECCIÓN: Iteramos sobre el mapa que creamos arriba
        for slug, real_name in slug_to_name_map.items():
            
            # Necesitamos los UUIDs. Usamos el endpoint ligero de Balena
            summary_devices = BalenaService.get_devices_by_fleet(slug)
            
            if not summary_devices: continue
            
            logger.info(f"⚡ Escaneando configuración de {len(summary_devices)} equipos en '{real_name}'...")

            # Creamos tareas paralelas SOLO para traer variables
            tasks = []
            for item in summary_devices:
                uuid = item.get("uuid")
                if uuid:
                    tasks.append(cls._worker_fetch_vars(uuid, semaphore))
            
            # Ejecutar lote
            results = await asyncio.gather(*tasks)
            
            # Aplanar resultados (lista de listas -> lista simple)
            batch_vars = []
            for res in results:
                if res:
                    batch_vars.extend(res)

            # Guardar en BD
            if batch_vars:
                await DeviceVarsRepository.upsert_batch(batch_vars)
                total_vars_processed += len(batch_vars)
                logger.info(f"   💾 {len(batch_vars)} variables guardadas de {real_name}")

        logger.info(f"🏁 CONFIGURACIÓN SINCRONIZADA. {total_vars_processed} variables procesadas.")
        return True

    @classmethod
    async def _worker_fetch_vars(cls, uuid, semaphore):
        """
        Hilo ligero: Solo pide variables a Balena para un UUID.
        """
        async with semaphore:
            try:
                # Ejecuta balena envs --device <uuid>
                vars_list = await asyncio.to_thread(BalenaService.get_device_vars, uuid)
                
                if not vars_list: return None
                
                # Mapeamos para el repo
                return [{
                    "uuid": uuid, 
                    "name": v.get("name"), 
                    "value": v.get("value")
                } for v in vars_list]

            except Exception as e:
                logger.error(f"⚠️ Error trayendo variables de {uuid}: {e}")
                return None
    
    @classmethod
    async def create_fleet_variable(cls, fleet_identifier: str, key: str, value: str):
        """
        Crea en Balena y guarda usando FleetVarsRepository.
        fleet_identifier: Debe ser el Nombre Real (ej: Andina_1) para que coincida con BD.
        """
        logger.info(f"🔧 Creando variable {key} en flota {fleet_identifier}...")
        
        if not BalenaService.login():
            return False

        # 1. Enviar a Balena (BalenaService ya no hace split, confía en el identificador)
        success = await asyncio.to_thread(BalenaService.set_fleet_variable, fleet_identifier, key, value)
        
        if not success:
            logger.error(f"❌ Balena rechazó la variable {key} para {fleet_identifier}")
            return False

        # 2. Guardar en BD Local REUTILIZANDO EL REPOSITORIO
        data_to_save = [{
            "fleet_slug": fleet_identifier, # Guardamos "Andina_1"
            "name": key,
            "value": value
        }]
        
        await FleetVarsRepository.upsert_batch(data_to_save)
        
        logger.info(f"✅ Variable {key} guardada en BD localmente.")
        return True

    @classmethod
    async def create_device_variable(cls, uuid: str, key: str, value: str):
        """
        Crea en Balena y guarda usando DeviceVarsRepository.
        """
        logger.info(f"🔧 Creando variable {key} en dispositivo {uuid}...")
        
        if not BalenaService.login():
            return False

        # 1. Enviar a Balena
        success = await asyncio.to_thread(BalenaService.set_device_variable, uuid, key, value)
        
        if not success:
            logger.error(f"❌ Balena rechazó la variable {key} para {uuid}")
            return False

        # 2. Guardar en BD Local REUTILIZANDO EL REPOSITORIO
        data_to_save = [{
            "uuid": uuid,
            "name": key,
            "value": value
        }]
        
        await DeviceVarsRepository.upsert_batch(data_to_save)
        
        logger.info(f"✅ Variable {key} guardada en BD localmente para {uuid}.")
        return True
    
    @classmethod
    async def sync_fleet_variables(cls, fleet_slug: str):
        """
        Sincroniza variables de UNA sola flota (Auto-Onboarding).
        """
        logger.info(f"🔧 Auto-Onboarding variables de flota: {fleet_slug}")
        if not BalenaService.login(): return False

        # Buscamos el nombre real
        raw_fleets = BalenaService.get_fleets()
        real_name = next((f.get("app_name") for f in raw_fleets if f.get("slug") == fleet_slug), None)
        
        if not real_name: return False

        vars_list = BalenaService.get_fleet_vars(fleet_slug)
        
        formatted_vars = []
        for v in vars_list:
            formatted_vars.append({
                "fleet_slug": real_name, 
                "name": v.get("name"),
                "value": v.get("value")
            })

        if formatted_vars:
            await FleetVarsRepository.upsert_batch(formatted_vars)
            logger.info(f"✅ Variables de {real_name} actualizadas.")
            
        return True

    @classmethod
    async def sync_device_variables(cls, uuid: str):
        """
        Sincroniza variables de UN solo dispositivo (Auto-Onboarding).
        """
        logger.info(f"🔧 Auto-Onboarding variables de dispositivo: {uuid}")
        if not BalenaService.login(): return False

        vars_list = BalenaService.get_device_vars(uuid)
        
        formatted_vars = []
        for v in vars_list:
            formatted_vars.append({
                "uuid": uuid,
                "name": v.get("name"),
                "value": v.get("value")
            })

        if formatted_vars:
            await DeviceVarsRepository.upsert_batch(formatted_vars)
            logger.info(f"✅ Variables de {uuid} actualizadas.")

        return True