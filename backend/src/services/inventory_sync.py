import logging
import asyncio 
from datetime import datetime, timezone
import json
from src.services.balena_service import BalenaService
from src.repositories.fleet_repo import FleetRepository
from src.repositories.info_devices_repo import InfoDevicesRepository
from src.repositories.history_repo import HistoryRepository
from src.utils.transaction_manager import TransactionManager, ScriptIds, TransactionStatus
from src.core.celery_app import celery_app 

logger = logging.getLogger(__name__)

class InventorySyncService:
    
    MAX_CONCURRENT_TASKS = 5 

    @classmethod
    async def sync_all(cls):
        logger.info(f"🚀 INICIANDO SINCRONIZACIÓN DE INVENTARIO (Max {cls.MAX_CONCURRENT_TASKS} hilos)...")
        
        if not BalenaService.login():
            logger.error("🛑 Abortado: Fallo login Balena.")
            return False

        # --- 1. INICIAR TRANSACCIÓN DE AUDITORÍA ---
        script_id = ScriptIds.AUTO_SYNC
        historic_id = await TransactionManager.start_transaction(script_id)
        
        try:
            # --- MEMORIA DEL SISTEMA ---
            existing_fleet_ids = await FleetRepository.get_all_ids()       
            existing_device_uuids = await InfoDevicesRepository.get_all_uuids()

            auto_onboarding_enabled = True
            if existing_fleet_ids is None or existing_device_uuids is None:
                logger.warning("⚠️ No se pudo leer la memoria (BD). Se DESACTIVA Auto-Onboarding.")
                auto_onboarding_enabled = False
                if existing_fleet_ids is None: existing_fleet_ids = set()
                if existing_device_uuids is None: existing_device_uuids = set()

            # --- PASO 1: FLOTAS ---
            raw_fleets = BalenaService.get_fleets()
            type_map = await FleetRepository.get_device_type_map()
            default_type_id = type_map.get('DEFAULT', 1) 

            fleets_to_save = []
            new_fleets_slugs_to_sync = [] 
            
            for f in raw_fleets:
                app_name = f.get("app_name") 
                slug = f.get("slug")
                balena_id = f.get("id")  # NUEVO: Capturar ID numérico inmutable
                remote_type_slug = f.get("device_type", "DEFAULT")
                mapped_id = type_map.get(remote_type_slug, default_type_id)

                if auto_onboarding_enabled and app_name and app_name not in existing_fleet_ids:
                    new_fleets_slugs_to_sync.append(slug) 
                    existing_fleet_ids.add(app_name)

                fleets_to_save.append({
                    "id": app_name, 
                    "balena_id": balena_id,  # NUEVO: Incluir ID de Balena
                    "slug": slug,
                    "device_type_id": mapped_id, 
                    "device_count": f.get("device_count", 0) 
                })
            
            if fleets_to_save:
                await FleetRepository.upsert_batch(fleets_to_save)

            for slug in new_fleets_slugs_to_sync:
                celery_app.send_task("tasks.sync_single_fleet_vars", args=[slug])


            # --- PASO 2: DISPOSITIVOS (PARALELO) ---
            total_devices_processed = 0
            
            # 👇 CONTADORES (Diccionario: FleetID -> {online, offline, reduced, free})
            fleet_stats = {f['id']: {'on': 0, 'off': 0, 'red': 0, 'free': 0} for f in fleets_to_save}
            fleet_stats['GENERAL'] = {'on': 0, 'off': 0, 'red': 0, 'free': 0} # Acumulador Global

            semaphore = asyncio.Semaphore(cls.MAX_CONCURRENT_TASKS)

            for fleet in fleets_to_save:
                fleet_slug = fleet["slug"]
                fleet_db_id = fleet["id"]
                
                summary_devices = BalenaService.get_devices_by_fleet(fleet_slug)
                if not summary_devices: continue
                
                logger.info(f"⚡ Procesando {len(summary_devices)} equipos en '{fleet_db_id}'...")

                tasks = []
                new_devices_uuids_to_sync = []

                for item in summary_devices:
                    uuid = item.get("uuid")
                    if uuid:
                        if auto_onboarding_enabled and uuid not in existing_device_uuids:
                            new_devices_uuids_to_sync.append(uuid)
                            existing_device_uuids.add(uuid)
                        tasks.append(cls._fetch_device_detail_concurrent(uuid, fleet_db_id, semaphore))
                
                results = await asyncio.gather(*tasks)
                devices_full_data = [r for r in results if r is not None]

                if devices_full_data:
                    # A. Guardar en BD (El repo ya espera 'device_status_id')
                    await InfoDevicesRepository.upsert_batch(devices_full_data)
                    
                    # B. Sumar a los contadores (Por Flota + Global)
                    for d in devices_full_data:
                        # Obtenemos el ID Específico (1-9)
                        sid = d.get("device_status_id", 3)
                        
                        inc_key = 'off' # Default
                        # Mapeamos a las 4 Categorías
                        if sid == 4: # Free
                            inc_key = 'free'
                        elif sid in [3, 8]: # Disconnected, Inactive -> OFFLINE
                            inc_key = 'off'
                        elif sid in [2, 9]: # Reduced, Frozen -> REDUCED
                            inc_key = 'red'
                        elif sid in [1, 5, 6, 7]: # Operational, Configuring, Updating, PostProv -> ONLINE
                            inc_key = 'on'
                        
                        # Incrementamos para la Flota y para General
                        fleet_stats[fleet_db_id][inc_key] += 1
                        fleet_stats['GENERAL'][inc_key] += 1

                    # C. Guardar Snapshot Individual
                    if historic_id:
                        for device_data in devices_full_data:
                            await HistoryRepository.log_device_snapshot(
                                historic_id, 
                                device_data['uuid'], 
                                TransactionStatus.COMPLETO, 
                                device_data 
                            )

                    total_devices_processed += len(devices_full_data)
                    
                    # D. Disparar variables para nuevos
                    for new_uuid in new_devices_uuids_to_sync:
                        celery_app.send_task("tasks.sync_single_device_vars", args=[new_uuid])

            # --- PASO 3: GUARDAR FOTO HISTÓRICA (POR FLOTA y GLOBAL) 📸 ---
            
            # Guardar GENERAL
            gen = fleet_stats['GENERAL']
            await HistoryRepository.log_global_stats(gen['on'], gen['off'], gen['red'], gen['free'], 'GENERAL')
            
            # Guardar Por Flota
            for fleet_id, stats in fleet_stats.items():
                if fleet_id == 'GENERAL': 
                    continue
                await HistoryRepository.log_global_stats(stats['on'], stats['off'], stats['red'], stats['free'], fleet_id)

            logger.info(f"📊 Stats Globales: Free={gen['free']}, Off={gen['off']}, On={gen['on']}, Red={gen['red']}")

            # --- CIERRE EXITOSO ---
            if historic_id:
                await TransactionManager.finish_transaction(
                    historic_id, 
                    script_id, 
                    TransactionStatus.COMPLETO, 
                    f"Sincronización finalizada. Equipos: {total_devices_processed}"
                )
            
            return True

        except Exception as e:
            logger.error(f"❌ Error crítico sync: {e}")
            if historic_id:
                await TransactionManager.finish_transaction(historic_id, script_id, TransactionStatus.FALLIDO, f"Error: {str(e)[:200]}")
            return False

    @classmethod
    async def _fetch_device_detail_concurrent(cls, uuid, fleet_slug, semaphore):
        async with semaphore:
            try:
                d = await asyncio.to_thread(BalenaService.get_device_detail, uuid)
                if not d: return None
                return cls._map_device_data(d, fleet_slug)
            except Exception as e:
                logger.warning(f"⚠️ Error procesando {uuid}: {e}")
                return None

    @classmethod
    def _map_device_data(cls, d, fleet_slug):
        def s_int(v): return int(float(v)) if v else 0

        # Datos Base
        api_hb = d.get("api_heartbeat_state") == "online"
        mem_mb = d.get("memory_usage_mb") or d.get("memory_usage")
        mem_total = d.get("memory_total_mb") or d.get("memory_total")
        storage_mb = d.get("storage_usage_mb") or d.get("storage_usage")
        storage_total = d.get("storage_total_mb") or d.get("storage_total")
        cpu_temp = d.get("cpu_temp_c") or d.get("cpu_temp")
        cpu_usage = d.get("cpu_usage_percent") or d.get("cpu_usage")
        
        note_val = d.get("note")
        if note_val is None:
            raw_note = ""
        else:
            raw_note = str(note_val)
        overall_status = str(d.get("overall_status") or "").strip().lower()
        is_online = d.get("is_online", False)

        # Default a Disconnected (3) si todo falla
        # Normalizamos: 'reduced-functionality' -> 'reduced functionality'
        status_clean = overall_status.replace('-', ' ')
        
        device_status_id = 3 

        # 1. FREE (Prioridad Absoluta) -> ID 4
        if "libre" in raw_note.lower():
            device_status_id = 4
        
        # 2. OFFLINE y REDUCED (Basado en overall_status)
        elif status_clean == 'inactive':
            device_status_id = 8
        elif status_clean == 'disconnected':
            device_status_id = 3
        elif status_clean == 'reduced functionality': 
            device_status_id = 2
        elif status_clean == 'frozen':
            device_status_id = 9
        
        # 3. ONLINE (Specific States)
        elif status_clean == 'operational':
            device_status_id = 1
        elif status_clean == 'configuring':
            device_status_id = 5
        elif status_clean == 'updating':
            device_status_id = 6
        elif status_clean == 'post provisioning':
            device_status_id = 7
        
        # 4. Fallback si está Online pero con status desconocido -> Operational (1)
        elif is_online:
            device_status_id = 1
        
        # 5. Fallback si está Offline -> Disconnected (3)
        else:
            device_status_id = 3
        # -----------------------------------------------------

        observaciones = {
            "mac_address": d.get("mac_address"),
            "public_address": d.get("public_address"),
            "dashboard_url": d.get("dashboard_url"),
            "cpu_id": d.get("cpu_id"),
            "overall_status_raw": overall_status 
        }

        return {
            "uuid": d.get("uuid"),
            
            # 👇 ESTE ES EL DATO QUE VA A LA BD ($23)
            "device_status_id": device_status_id, 
            
            # Compatibilidad Legacy (Si tu repo aun usa status_id antiguo)
            "status_id": 1, 
            
            "service_id": "1111", 
            "device_name": d.get("device_name"),
            "is_online": is_online,
            "api_heartbeat": api_hb,
            "last_connectivity": cls._parse_date(d.get("last_connectivity_event")),
            "fleet_id": fleet_slug,
            "supervisor_version": d.get("supervisor_version"),
            "os_version": d.get("os_version"),
            "note": raw_note, 
            "memory_usage": s_int(mem_mb),
            "memory_total": s_int(mem_total),
            "storage_usage": s_int(storage_mb),
            "storage_total": s_int(storage_total),
            "cpu_temp": s_int(cpu_temp),
            "cpu_usage": s_int(cpu_usage),
            "last_metric_update": datetime.now(timezone.utc),
            "ip_address": d.get("ip_address"),
            "vpn_connected": d.get("is_connected_to_vpn", False),
            "last_vpn_event": cls._parse_date(d.get("last_vpn_event")),
            "observaciones": observaciones
        }

    @staticmethod
    def _parse_date(date_str):
        if not date_str: return datetime.now(timezone.utc)
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now(timezone.utc)

    @classmethod
    async def sync_single_fleet(cls, fleet_id: str, user: str = "SYSTEM", role: str = "SYSTEM"):
        """
        Sincroniza solo los dispositivos de una flota específica.
        Más rápido y eficiente que sync_all().
        
        Args:
            fleet_id: ID de la flota en la BD (app_name)
            user: Usuario que ejecuta la sincronización
            role: Rol del usuario
            
        Returns:
            dict con success, devices_synced, y mensaje
        """
        logger.info(f"🔄 Sincronizando flota: {fleet_id}")
        
        # Verificar login a Balena
        if not BalenaService.login():
            raise Exception("Fallo login Balena")
        
        # Iniciar transacción
        script_id = ScriptIds.MANUAL_SYNC
        historic_id = await TransactionManager.start_transaction(script_id, user, role)
        
        if not historic_id:
            raise Exception("No se pudo iniciar la transacción (posiblemente ya hay una en progreso)")
        
        try:
            # Obtener datos de la flota desde BD
            fleet_data = await FleetRepository.get_by_id(fleet_id)
            if not fleet_data:
                raise Exception(f"Flota {fleet_id} no encontrada en BD")
            
            fleet_slug = fleet_data.get('slug')
            if not fleet_slug:
                raise Exception(f"Flota {fleet_id} no tiene slug")
            
            logger.info(f"📡 Consultando Balena para flota '{fleet_id}' (slug: {fleet_slug})...")
            
            # Obtener dispositivos de Balena para esta flota
            summary_devices = BalenaService.get_devices_by_fleet(fleet_slug)
            if not summary_devices:
                logger.warning(f"⚠️ No se encontraron dispositivos en Balena para {fleet_id}")
                await TransactionManager.finish_transaction(
                    historic_id, script_id, TransactionStatus.COMPLETO,
                    f"Sincronización completada. 0 dispositivos encontrados en {fleet_id}"
                )
                return {"success": True, "devices_synced": 0, "message": "No hay dispositivos en esta flota"}
            
            logger.info(f"⚡ Procesando {len(summary_devices)} equipos en '{fleet_id}'...")
            
            # Procesar dispositivos en paralelo
            semaphore = asyncio.Semaphore(cls.MAX_CONCURRENT_TASKS)
            tasks = []
            devices_to_save = []
            
            # Contadores para estadísticas
            stats = {'on': 0, 'off': 0, 'red': 0, 'free': 0}
            
            for item in summary_devices:
                uuid = item.get("uuid")
                if uuid:
                    tasks.append(cls._fetch_device_detail_concurrent(uuid, fleet_id, semaphore))
            
            # Ejecutar todas las tareas en paralelo
            results = await asyncio.gather(*tasks)
            
            # Filtrar resultados válidos y contar estados
            for device_data in results:
                if device_data:
                    devices_to_save.append(device_data)
                    
                    # Contar por estado
                    status_id = device_data.get('status_id', 0)
                    if status_id == 1:  # Operativo
                        stats['on'] += 1
                    elif status_id == 2:  # Reducido
                        stats['red'] += 1
                    elif status_id == 3:  # Desconectado
                        stats['off'] += 1
                    elif status_id == 4:  # Libre
                        stats['free'] += 1
            
            # Guardar dispositivos en BD
            if devices_to_save:
                await InfoDevicesRepository.upsert_batch(devices_to_save)
                logger.info(f"💾 Guardados {len(devices_to_save)} dispositivos de {fleet_id}")
            
            # Guardar estadísticas para esta flota específica
            await HistoryRepository.log_global_stats(
                stats['on'], stats['off'], stats['red'], stats['free'], fleet_id
            )
            
            # También actualizar estadísticas GENERAL
            await HistoryRepository.log_global_stats(
                stats['on'], stats['off'], stats['red'], stats['free'], 'GENERAL'
            )
            
            # Finalizar transacción exitosamente
            await TransactionManager.finish_transaction(
                historic_id, script_id, TransactionStatus.COMPLETO,
                f"Sincronización completada. {len(devices_to_save)} dispositivos procesados en {fleet_id}"
            )
            
            logger.info(f"✅ Sincronización de {fleet_id} completada: {len(devices_to_save)} dispositivos")
            
            return {
                "success": True,
                "devices_synced": len(devices_to_save),
                "message": f"Flota {fleet_id} sincronizada exitosamente",
                "stats": stats
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Error sincronizando flota {fleet_id}: {error_msg}")
            await TransactionManager.finish_transaction(
                historic_id, script_id, TransactionStatus.FALLIDO, error_msg
            )
            raise
