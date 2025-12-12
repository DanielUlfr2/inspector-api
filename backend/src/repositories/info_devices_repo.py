import json
import logging
from databases.postgres_connector import PostgresConnector
from src.core.security import SecurityValidator
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class InfoDevicesRepository:
    
    @staticmethod
    async def get_all_devices():
        query = 'SELECT * FROM inspector."Inspector"'
        conn = await PostgresConnector.get_connection()
        try:
            return await conn.fetch(query)
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def upsert_batch(devices_data: List[Dict[str, Any]]):
        if not devices_data:
            return

        # Query masivo optimizado (Upsert)
        query = """
            INSERT INTO inspector."Inspector" (
                "uuidInspector", "idInventoryInspectorStatus", "strInspectorServiceId",
                "strInspectorName", "boolOnline", "boolApiHearbeatState", 
                "dtLastConnectivityEvent", "stridInspectorFleet", "strSupervisorVersion", 
                "strOsVersion", "strNote", "intMemoryUsageMB", "intMemoryTotalMB", 
                "intStorageUsageMB", "intStorageTotalMB", "intCpuTempC", 
                "intCpuUsagePercent", "dtLastMetricUpdate", "strIpAddress", 
                "boolConnectedToVpn", "dtLastVpnEvent", "jsonbObservaciones", "dtDateCreate", "dtModificationDate"
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, NOW(), NOW()
            )
            ON CONFLICT ("uuidInspector") DO UPDATE SET
                "strInspectorName" = EXCLUDED."strInspectorName",
                "boolOnline" = EXCLUDED."boolOnline",
                "dtLastConnectivityEvent" = EXCLUDED."dtLastConnectivityEvent",
                "strIpAddress" = EXCLUDED."strIpAddress",
                "intMemoryUsageMB" = EXCLUDED."intMemoryUsageMB",
                "intCpuTempC" = EXCLUDED."intCpuTempC",
                "dtModificationDate" = NOW();
        """

        # Preparar los valores (Mapeo JSON -> Tupla SQL)
        values = []
        for d in devices_data:
            # Validamos Strings
            d = SecurityValidator.sanitize_input(d)
            
            values.append((
                d["uuid"],
                d.get("status_id", 1), # Default ID status
                d.get("service_id", "Unknown"), 
                d.get("device_name", "Sin Nombre"),
                d.get("is_online", False),
                d.get("api_heartbeat", False),
                d.get("last_connectivity"),
                d.get("fleet_id"), # Link a la flota
                d.get("supervisor_version"),
                d.get("os_version"),
                d.get("note"),
                d.get("memory_usage", 0),
                d.get("memory_total", 0),
                d.get("storage_usage", 0),
                d.get("storage_total", 0),
                d.get("cpu_temp", 0),
                d.get("cpu_usage", 0),
                d.get("last_metric_update"),
                d.get("ip_address"),
                d.get("vpn_connected", False),
                d.get("last_vpn_event"),
                json.dumps(d.get("observaciones", {}))
            ))

        conn = await PostgresConnector.get_connection()
        try:
            await conn.executemany(query, values)
            logger.info(f"✅ {len(values)} inspectores (dispositivos) sincronizados.")
        except Exception as e:
            logger.error(f"❌ Error insertando inspectores: {e}")
        finally:
            await PostgresConnector.release_connection(conn)