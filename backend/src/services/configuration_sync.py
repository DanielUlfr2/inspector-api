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
        # Lista simple de slugs para usar en la fase 2
        fleet_slugs = [] 

        for f in raw_fleets:
            slug = f.get("slug")
            if not slug: continue
            
            fleet_slugs.append(slug)
            
            # Traer variables de esta flota
            vars_list = BalenaService.get_fleet_vars(slug)
            for v in vars_list:
                all_fleet_vars.append({
                    "fleet_slug": slug,
                    "name": v.get("name"),
                    "value": v.get("value")
                })
        
        # Guardar masivamente variables de flota
        if all_fleet_vars:
            await FleetVarsRepository.upsert_batch(all_fleet_vars)
            logger.info(f"✅ Guardadas {len(all_fleet_vars)} variables de flotas.")

        # --- FASE 2: VARIABLES DE DISPOSITIVOS (PARALELO) ---
        total_vars_processed = 0
        semaphore = asyncio.Semaphore(cls.MAX_CONCURRENT_TASKS)

        for slug in fleet_slugs:
            # Necesitamos los UUIDs. Usamos el endpoint ligero de Balena solo para obtener la lista.
            summary_devices = BalenaService.get_devices_by_fleet(slug)
            
            if not summary_devices: continue
            
            logger.info(f"⚡ Escaneando configuración de {len(summary_devices)} equipos en '{slug}'...")

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
                logger.info(f"   💾 {len(batch_vars)} variables guardadas de {slug}")

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