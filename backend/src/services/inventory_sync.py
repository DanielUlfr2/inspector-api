import logging
from datetime import datetime
from src.services.balena_service import BalenaService
from src.repositories.fleet_repo import FleetRepository
from src.repositories.info_devices_repo import InfoDevicesRepository

logger = logging.getLogger(__name__)

class InventorySyncService:
    
    @classmethod
    async def sync_all(cls):
        logger.info("🚀 INICIANDO SINCRONIZACIÓN INTELIGENTE (Datos Reales)")
        
        # 1. Login
        if not BalenaService.login():
            logger.error("🛑 Abortado: Fallo login Balena.")
            return

        # 2. Obtener y Guardar Flotas
        raw_fleets = BalenaService.get_fleets()
        fleets_to_save = []
        
        # Mapa para buscar ID de flota por Slug rápidamente
        fleet_slug_map = {} 

        for f in raw_fleets:
            # En tu JSON de dispositivo, la flota se referencia por slug o nombre.
            # Aseguramos guardar el slug como ID si así lo usas, o el ID numérico.
            # Basado en tu comentario: "app seria la flota slug"
            fleet_id = f.get("slug") # Ej: admin/andina_2
            
            fleets_to_save.append({
                "id": fleet_id,
                "slug": f.get("slug"),
                "device_type": f.get("device_type"),
                "device_count": len(f.get("owns__device", []))
            })
            fleet_slug_map[f.get("slug")] = fleet_id

        await FleetRepository.upsert_batch(fleets_to_save)
        logger.info(f"✅ {len(fleets_to_save)} flotas actualizadas.")

        # 3. Sincronizar Dispositivos
        total_devices = 0
        
        # Iteramos sobre las flotas que acabamos de guardar
        for fleet in fleets_to_save:
            fleet_slug = fleet["slug"]
            
            # Traemos el JSON crudo que me mostraste
            raw_devices = BalenaService.get_devices_by_fleet(fleet_slug)
            
            if not raw_devices:
                continue
            
            devices_to_save = []
            for d in raw_devices:
                
                # --- LÓGICA DE MAPEO EXACTA (Tu JSON -> BD) ---
                
                # 1. Determinar la Flota (FK)
                # El JSON tiene: "belongs_to__application": [{"slug": "admin/andina_2"}]
                apps = d.get("belongs_to__application", [])
                fleet_fk = apps[0].get("slug") if apps else fleet_slug
                
                # 2. Determinar Heartbeat
                api_hb = d.get("api_heartbeat_state") == "online"
                
                # 3. Datos de Observaciones (Metemos MAC y otros extras aquí)
                observaciones = {
                    "mac_address": d.get("mac_address"),
                    "public_address": d.get("public_address"),
                    "dashboard_url": d.get("dashboard_url"),
                    "cpu_id": d.get("cpu_id")
                }

                devices_to_save.append({
                    # Identificadores
                    "uuid": d.get("uuid"),
                    
                    # --- CAMPOS POR DEFECTO (NEGOCIO) ---
                    "status_id": 1,         # Default: Ocupado/Activo
                    "service_id": "1111",   # Default: Dummy Service
                    
                    # --- CAMPOS TÉCNICOS (REALES DE BALENA) ---
                    "device_name": d.get("device_name"),
                    "is_online": d.get("is_online", False),
                    "api_heartbeat": api_hb,
                    "last_connectivity": cls._parse_date(d.get("last_connectivity_event")),
                    
                    "fleet_id": fleet_fk,   # FK Real
                    
                    "supervisor_version": d.get("supervisor_version"),
                    "os_version": d.get("os_version"),
                    
                    # Nota: El JSON trae "4C:12:..." en note. Lo guardamos.
                    "note": d.get("note"), 
                    
                    # Recursos
                    "memory_usage": d.get("memory_usage_mb", 0),
                    "memory_total": d.get("memory_total_mb", 0),
                    "storage_usage": d.get("storage_usage_mb", 0),
                    "storage_total": d.get("storage_total_mb", 0),
                    "cpu_temp": d.get("cpu_temp_c", 0),
                    "cpu_usage": d.get("cpu_usage_percent", 0),
                    
                    "last_metric_update": datetime.now(), # Balena no trae fecha de métrica exacta, usamos NOW
                    
                    "ip_address": d.get("ip_address"), # Ej: "192.168.1.6 2800:..."
                    "vpn_connected": d.get("is_connected_to_vpn", False),
                    "last_vpn_event": cls._parse_date(d.get("last_vpn_event")),
                    
                    # Extras
                    "observaciones": observaciones
                })
            
            await InfoDevicesRepository.upsert_batch(devices_to_save)
            total_devices += len(devices_to_save)

        logger.info(f"🏁 SINCRONIZACIÓN FINALIZADA. {total_devices} dispositivos procesados.")

    @staticmethod
    def _parse_date(date_str):
        if not date_str:
            return datetime.now()
        try:
            # Maneja formato "2025-12-12T02:17:38.441Z"
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return datetime.now()