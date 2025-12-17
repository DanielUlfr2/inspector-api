import logging
import asyncio 
from datetime import datetime, timezone
import json
from src.services.balena_service import BalenaService
from src.repositories.fleet_repo import FleetRepository
from src.repositories.info_devices_repo import InfoDevicesRepository
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
        
        # ### [NUEVO] 1. TRAEMOS EL MAPA DE TRADUCCIÓN (Slug -> ID)
        # Esto convierte "raspberrypi4-64" -> 3
        type_map = await FleetRepository.get_device_type_map()
        # Si llega un tipo raro que no tenemos, le ponemos el ID 1 (DEFAULT)
        default_type_id = type_map.get('DEFAULT', 1) 

        fleets_to_save = []
        new_fleets_slugs_to_sync = [] 
        
        for f in raw_fleets:
            app_name = f.get("app_name") 
            slug = f.get("slug")
            
            # ### [NUEVO] 2. TRADUCIMOS EL TIPO DE DISPOSITIVO
            remote_type_slug = f.get("device_type", "DEFAULT")
            mapped_id = type_map.get(remote_type_slug, default_type_id)

            # Detección (Sin disparar todavía)
            if auto_onboarding_enabled and app_name and app_name not in existing_fleet_ids:
                new_fleets_slugs_to_sync.append(slug) 
                existing_fleet_ids.add(app_name)

            fleets_to_save.append({
                "id": app_name, 
                "slug": slug,
                # ### [CAMBIO] Usamos la llave 'device_type_id' con el valor numérico
                "device_type_id": mapped_id, 
                "device_count": f.get("device_count", 0) 
            })
        
        # 1. GUARDAMOS FLOTAS EN BD
        if fleets_to_save:
            await FleetRepository.upsert_batch(fleets_to_save)
            logger.info(f"✅ {len(fleets_to_save)} flotas actualizadas.")

        # 2. DISPARAR TAREAS
        for slug in new_fleets_slugs_to_sync:
            logger.info(f"🆕 Nueva Flota detectada. Pidiendo variables para: {slug}")
            celery_app.send_task("tasks.sync_single_fleet_vars", args=[slug])


        # --- PASO 2: DISPOSITIVOS (PARALELO) ---
        total_devices_processed = 0
        semaphore = asyncio.Semaphore(cls.MAX_CONCURRENT_TASKS)

        for fleet in fleets_to_save:
            fleet_slug = fleet["slug"]
            fleet_db_id = fleet["id"]
            
            summary_devices = BalenaService.get_devices_by_fleet(fleet_slug)
            
            if not summary_devices: continue
            
            logger.info(f"⚡ Procesando {len(summary_devices)} equipos en '{fleet_slug}'...")

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
                # 3. GUARDAMOS DISPOSITIVOS
                await InfoDevicesRepository.upsert_batch(devices_full_data)
                total_devices_processed += len(devices_full_data)
                logger.info(f"   💾 Guardados {len(devices_full_data)} dispositivos de {fleet_slug}")

                # 4. DISPARAMOS VARIABLES
                for new_uuid in new_devices_uuids_to_sync:
                    logger.info(f"🆕 Nuevo Equipo guardado. Pidiendo variables para: {new_uuid}")
                    celery_app.send_task("tasks.sync_single_device_vars", args=[new_uuid])

        logger.info(f"🏁 SINCRONIZACIÓN FINALIZADA. {total_devices_processed} dispositivos procesados.")
        return True

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
        api_hb = d.get("api_heartbeat_state") == "online"
        def s_int(v): return int(float(v)) if v else 0

        mem_mb = d.get("memory_usage_mb") or d.get("memory_usage")
        mem_total = d.get("memory_total_mb") or d.get("memory_total")
        storage_mb = d.get("storage_usage_mb") or d.get("storage_usage")
        storage_total = d.get("storage_total_mb") or d.get("storage_total")
        cpu_temp = d.get("cpu_temp_c") or d.get("cpu_temp")
        cpu_usage = d.get("cpu_usage_percent") or d.get("cpu_usage")

        observaciones = {
            "mac_address": d.get("mac_address"),
            "public_address": d.get("public_address"),
            "dashboard_url": d.get("dashboard_url"),
            "cpu_id": d.get("cpu_id")
        }

        return {
            "uuid": d.get("uuid"),
            "status_id": 1, 
            "service_id": "1111", 
            "device_name": d.get("device_name"),
            "is_online": d.get("is_online", False),
            "api_heartbeat": api_hb,
            "last_connectivity": cls._parse_date(d.get("last_connectivity_event")),
            "fleet_id": fleet_slug,
            "supervisor_version": d.get("supervisor_version"),
            "os_version": d.get("os_version"),
            "note": d.get("note"), 
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
        if not date_str:
            return datetime.now(timezone.utc)
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now(timezone.utc)