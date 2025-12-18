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
    
    @staticmethod
    async def update_device_note(uuid: str, note: str):
        """
        Actualiza solo el campo de nota en la BD local.
        """
        query = "UPDATE inspector.inspector SET strnote = $1, dtmodificationdate = NOW() WHERE uuidinspector = $2"
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, note, uuid)
            logger.info(f"✅ DB: Nota actualizada para {uuid}")
            return True
        except Exception as e:
            logger.error(f"❌ Error DB update note: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)
    
    @staticmethod
    async def get_device_by_uuid(uuid: str) -> Dict[str, Any]:
        """
        Retorna el estado actual registrado en BD de un equipo.
        Usado para generar el snapshot en el historial antes de una acción.
        """
        query = """
            SELECT 
                boolonline as is_online,
                intmemoryusagemb as memory_usage,
                intmemorytotalmb as memory_total,
                intstorageusagemb as storage_usage,
                intstoragetotalmb as storage_total,
                intcputempc as cpu_temp,
                intcpuusagepercent as cpu_usage
            FROM inspector.inspector 
            WHERE uuidinspector = $1
        """
        conn = await PostgresConnector.get_connection()
        try:
            record = await conn.fetchrow(query, uuid)
            return dict(record) if record else {}
        except Exception as e:
            logger.error(f"❌ Error obteniendo snapshot de dispositivo {uuid}: {e}")
            return {}
        finally:
            await PostgresConnector.release_connection(conn)
    
    @staticmethod
    async def get_device_history_range(uuid: str, start_date: datetime, end_date: datetime):
        """
        Obtiene el historial de métricas (CPU, RAM, Temp) para gráficas.
        """
        query = """
            SELECT 
                dtValidate as timestamp,
                boolOnline as is_online,
                intHistoryMemoryUsageMB as memory_usage,
                intHistoryCpuUsagePercent as cpu_usage,
                intHistoryCpuTempC as cpu_temp,
                intHistoryStorageUsageMB as storage_usage
            FROM inspector.StatusInspectorHistory
            WHERE uuidInspector = $1
              AND dtValidate BETWEEN $2 AND $3
            ORDER BY dtValidate ASC
        """
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query, uuid, start_date, end_date)
            # Convertimos a lista de diccionarios limpia para el JSON
            return [dict(r) for r in records]
        except Exception as e:
            logger.error(f"❌ Error fetching history for {uuid}: {e}")
            return []
        finally:
            await PostgresConnector.release_connection(conn)
    
    @staticmethod
    async def get_device_detail_full(uuid: str):
        """
        Obtiene la ficha técnica COMPLETA haciendo JOIN con Status y Service.
        """
        # AJUSTE: Usamos las columnas reales de tus tablas
        query = """
            SELECT 
                i.*,
                st.strInventoryStatus as status_name, 
                ser.strClientName as service_name
            FROM inspector.Inspector i
            LEFT JOIN inspector.InventoryInspectorStatus st 
                ON i.idInventoryInspectorStatus = st.idInventoryInspectorStatus
            LEFT JOIN inspector.InspectorService ser 
                ON i.strInspectorServiceId = ser.strInspectorServiceId
            WHERE i.uuidInspector = $1
        """
        
        conn = await PostgresConnector.get_connection()
        try:
            record = await conn.fetchrow(query, uuid)
            if record:
                # Convertimos a dict
                data = dict(record)
                
                # Parsear JSON de observaciones si viene como texto
                if isinstance(data.get('jsonbobservaciones'), str):
                     import json
                     data['jsonbobservaciones'] = json.loads(data['jsonbobservaciones'])
                
                # [OPCIONAL] Si algún campo de fecha viene con zona horaria, limpiarlo aquí
                # (Pydantic suele manejarlo bien, pero por seguridad):
                if data.get('dtlastconnectivityevent'):
                    data['dtlastconnectivityevent'] = data['dtlastconnectivityevent'].replace(tzinfo=None)
                
                return data
            return None
        finally:
            await PostgresConnector.release_connection(conn)
    
    @staticmethod
    async def update_device_fleet(uuid: str, new_fleet_slug: str):
        """
        Actualiza la flota del dispositivo en la BD local.
        """
        query = """
            UPDATE inspector.Inspector 
            SET stridInspectorFleet = $1, 
                dtModificationDate = NOW() 
            WHERE uuidInspector = $2
        """
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, new_fleet_slug, uuid)
            logger.info(f"✅ DB: Dispositivo {uuid} movido a flota {new_fleet_slug}")
            return True
        except Exception as e:
            logger.error(f"❌ Error DB update fleet: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)