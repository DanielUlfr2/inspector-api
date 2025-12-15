import logging
import json
from datetime import datetime, timezone
from databases.postgres_connector import PostgresConnector
from src.core.security import SecurityValidator
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class InfoDevicesRepository:
    
    @staticmethod
    def prepare_date_for_db(dt_val):
        """
        Adapta la fecha para columnas TIMESTAMP (Sin Zona Horaria).
        1. Si es None, retorna None.
        2. Si tiene zona horaria (Aware), la convierte a UTC y le QUITA la zona (Naive).
        """
        if dt_val is None:
            return None
        
        if not isinstance(dt_val, datetime):
            return dt_val
        
        # Si tiene zona horaria (ej: UTC), se la quitamos para que Postgres no llore
        if dt_val.tzinfo is not None:
            # Convertimos a UTC puro y luego removemos la info de zona
            return dt_val.astimezone(timezone.utc).replace(tzinfo=None)
        
        return dt_val

    @staticmethod
    async def upsert_batch(devices_data: List[Dict[str, Any]]):
        if not devices_data:
            return

        # Query ajustada a tu esquema
        query = """
            INSERT INTO inspector.inspector (
                uuidinspector, idinventoryinspectorstatus, strinspectorserviceid,
                strinspectorname, boolonline, boolapihearbeatstate, 
                dtlastconnectivityevent, stridinspectorfleet, strsupervisorversion, 
                strosversion, strnote, intmemoryusagemb, intmemorytotalmb, 
                intstorageusagemb, intstoragetotalmb, intcputempc, 
                intcpuusagepercent, dtlastmetricupdate, stripaddress, 
                boolconnectedtovpn, dtlastvpnevent, jsonbobservaciones,
                dtdatecreate, dtmodificationdate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, NOW(), NOW()
            )
            ON CONFLICT (uuidinspector) DO UPDATE SET
                strinspectorname = EXCLUDED.strinspectorname,
                boolonline = EXCLUDED.boolonline,
                boolapihearbeatstate = EXCLUDED.boolapihearbeatstate,
                dtlastconnectivityevent = EXCLUDED.dtlastconnectivityevent,
                stripaddress = EXCLUDED.stripaddress,
                strnote = EXCLUDED.strnote,
                intmemoryusagemb = EXCLUDED.intmemoryusagemb,
                intmemorytotalmb = EXCLUDED.intmemorytotalmb,
                intstorageusagemb = EXCLUDED.intstorageusagemb,
                intstoragetotalmb = EXCLUDED.intstoragetotalmb,
                intcputempc = EXCLUDED.intcputempc,
                intcpuusagepercent = EXCLUDED.intcpuusagepercent,
                dtlastmetricupdate = EXCLUDED.dtlastmetricupdate,
                dtmodificationdate = NOW();
        """

        values = []
        for d in devices_data:
            d = SecurityValidator.sanitize_input(d)
            
            obs_json = json.dumps(d.get("observaciones", {})) 

            # --- LIMPIEZA DE FECHAS (QUITAR ZONA HORARIA) ---
            # $7
            last_conn = InfoDevicesRepository.prepare_date_for_db(d.get("last_connectivity"))
            # Si last_conn es None (y la BD es NOT NULL), ponemos la hora actual sin zona
            if last_conn is None:
                last_conn = datetime.utcnow()

            # $18
            last_metric = InfoDevicesRepository.prepare_date_for_db(d.get("last_metric_update"))
            
            # $21
            last_vpn = InfoDevicesRepository.prepare_date_for_db(d.get("last_vpn_event"))
            # ------------------------------------------------

            values.append((
                d["uuid"],
                d.get("status_id", 1),
                d.get("service_id", "1111"), 
                d.get("device_name", "Sin Nombre"),
                d.get("is_online", False),
                d.get("api_heartbeat", False),
                
                last_conn, # $7 (Naive Datetime)
                
                d.get("fleet_id"), 
                d.get("supervisor_version"),
                d.get("os_version"),
                d.get("note"),
                d.get("memory_usage", 0),
                d.get("memory_total", 0),
                d.get("storage_usage", 0),
                d.get("storage_total", 0),
                d.get("cpu_temp", 0),
                d.get("cpu_usage", 0),
                
                last_metric, # $18 (Naive Datetime)
                
                d.get("ip_address"),
                d.get("vpn_connected", False),
                
                last_vpn, # $21 (Naive Datetime)
                
                obs_json 
            ))

        conn = await PostgresConnector.get_connection()
        try:
            await conn.executemany(query, values)
            logger.info(f"✅ {len(values)} inspectores (dispositivos) sincronizados.")
        except Exception as e:
            logger.error(f"❌ Error insertando inspectores: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)
    
    @staticmethod
    async def get_all_uuids():
        """
        Retorna un SET con todos los UUIDs.
        SEGURIDAD: Retorna None si falla.
        """
        query = 'SELECT uuidinspector FROM inspector.inspector;'
        
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            return {r["uuidinspector"] for r in records}
        except Exception as e:
            logger.error(f"❌ Error CRÍTICO obteniendo UUIDs: {e}")
            return None # <--- CAMBIO: Retornar None en vez de set()
        finally:
            await PostgresConnector.release_connection(conn)