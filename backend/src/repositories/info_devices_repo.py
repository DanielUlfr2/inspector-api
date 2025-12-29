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
        """
        if dt_val is None:
            return None
        
        if not isinstance(dt_val, datetime):
            return dt_val
        
        # Si tiene zona horaria (ej: UTC), se la quitamos para que Postgres no llore
        if dt_val.tzinfo is not None:
            return dt_val.astimezone(timezone.utc).replace(tzinfo=None)
        
        return dt_val

    @staticmethod
    async def upsert_batch(devices_data: List[Dict[str, Any]]):
        if not devices_data:
            return

        # Query ajustada a tu nuevo esquema SQL
        query = """
            INSERT INTO inspector.inspector (
                uuidinspector, 
                idinventoryinspectorstatus, -- Status original
                strinspectorserviceid,
                strinspectorname, 
                boolonline, 
                boolapihearbeatstate, 
                dtlastconnectivityevent, 
                stridinspectorfleet, 
                strsupervisorversion, 
                strosversion, 
                strnote, 
                intmemoryusagemb, 
                intmemorytotalmb, 
                intstorageusagemb, 
                intstoragetotalmb, 
                intcputempc, 
                intcpuusagepercent, 
                dtlastmetricupdate, 
                stripaddress, 
                boolconnectedtovpn, 
                dtlastvpnevent, 
                jsonbobservaciones,
                idDeviceStatus,             -- 👈 NUEVA COLUMNA (INT)
                dtdatecreate, 
                dtmodificationdate
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 
                $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, 
                $21, $22, 
                $23,                        -- 👈 Placeholder para idDeviceStatus
                NOW(), NOW()
            )
            ON CONFLICT (uuidinspector) DO UPDATE SET
                idinventoryinspectorstatus = EXCLUDED.idinventoryinspectorstatus,
                strinspectorname = EXCLUDED.strinspectorname,
                boolonline = EXCLUDED.boolonline,
                boolapihearbeatstate = EXCLUDED.boolapihearbeatstate,
                dtlastconnectivityevent = EXCLUDED.dtlastconnectivityevent,
                stridinspectorfleet = EXCLUDED.stridinspectorfleet,
                stripaddress = EXCLUDED.stripaddress,
                strnote = EXCLUDED.strnote,
                intmemoryusagemb = EXCLUDED.intmemoryusagemb,
                intmemorytotalmb = EXCLUDED.intmemorytotalmb,
                intstorageusagemb = EXCLUDED.intstorageusagemb,
                intstoragetotalmb = EXCLUDED.intstoragetotalmb,
                intcputempc = EXCLUDED.intcputempc,
                intcpuusagepercent = EXCLUDED.intcpuusagepercent,
                boolconnectedtovpn = EXCLUDED.boolconnectedtovpn,
                dtlastmetricupdate = EXCLUDED.dtlastmetricupdate,
                idDeviceStatus = EXCLUDED.idDeviceStatus,  -- 👈 Actualizamos el estado calculado
                dtmodificationdate = NOW();
        """

        values = []
        for d in devices_data:
            d = SecurityValidator.sanitize_input(d)
            
            obs_json = json.dumps(d.get("observaciones", {})) 

            # --- LIMPIEZA DE FECHAS ---
            # $7 Last Connectivity
            last_conn = InfoDevicesRepository.prepare_date_for_db(d.get("last_connectivity"))
            if last_conn is None: last_conn = datetime.utcnow()

            # $18 Last Metric
            last_metric = InfoDevicesRepository.prepare_date_for_db(d.get("last_metric_update"))
            if last_metric is None: last_metric = datetime.utcnow()
            
            # $21 Last VPN
            last_vpn = InfoDevicesRepository.prepare_date_for_db(d.get("last_vpn_event"))
            if last_vpn is None: last_vpn = datetime.utcnow()
            # --------------------------

            values.append((
                d["uuid"],                          # $1
                d.get("status_id", 1),              # $2 (Este es el idInventoryInspectorStatus viejo)
                d.get("service_id", "1111"),        # $3
                d.get("device_name") or "Sin Nombre", # $4
                d.get("is_online", False),          # $5
                d.get("api_heartbeat", False),      # $6
                
                last_conn,                          # $7
                
                d.get("fleet_id"),                  # $8
                d.get("supervisor_version") or "",  # $9
                d.get("os_version") or "",          # $10
                d.get("note") or "",                # $11
                d.get("memory_usage", 0),           # $12
                d.get("memory_total", 0),           # $13
                d.get("storage_usage", 0),          # $14
                d.get("storage_total", 0),          # $15
                d.get("cpu_temp", 0),               # $16
                d.get("cpu_usage", 0),              # $17
                
                last_metric,                        # $18
                
                d.get("ip_address"),                # $19
                d.get("vpn_connected", False),      # $20
                
                last_vpn,                           # $21
                
                obs_json,                           # $22
                
                d.get("device_status_id", 2)        # $23 👈 idDeviceStatus (1=On, 2=Off, 3=Red, 4=Free)
                                                    # Ponemos 2 (Offline) como default seguro
            ))

        conn = await PostgresConnector.get_connection()
        try:
            await conn.executemany(query, values)
            logger.info(f"✅ {len(values)} inspectores sincronizados.")
        except Exception as e:
            logger.error(f"❌ Error insertando inspectores: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)

    # ... (El resto de métodos de la clase se mantienen IGUALES) ...
    # get_all_uuids, update_device_note, get_device_by_uuid, etc.
    
    @staticmethod
    async def get_all_devices() -> List[Dict[str, Any]]:
        query = """
            SELECT 
                uuidinspector, 
                strinspectorname, 
                idinventoryinspectorstatus, 
                boolonline, 
                stridinspectorfleet, 
                stripaddress, 
                dtlastconnectivityevent, 
                strosversion, 
                jsonbobservaciones,
                strnote,
                idDeviceStatus AS iddevicestatus
            FROM inspector.inspector
        """
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            # Convert record objects to dictionaries and handle JSON/Date parsing if needed
            result = []
            for r in records:
                d = dict(r)
                if isinstance(d.get('jsonbobservaciones'), str):
                     import json
                     d['jsonbobservaciones'] = json.loads(d['jsonbobservaciones'])
                
                # Manejo de fechas para evitar problemas de tz
                if d.get('dtlastconnectivityevent') and d['dtlastconnectivityevent'].tzinfo:
                     d['dtlastconnectivityevent'] = d['dtlastconnectivityevent'].replace(tzinfo=None)

                result.append(d)
            return result
        except Exception as e:
            logger.error(f"❌ Error fetching all devices: {e}")
            return []
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def get_all_uuids():
        query = 'SELECT uuidinspector FROM inspector.inspector;'
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            return {r["uuidinspector"] for r in records}
        except Exception as e:
            logger.error(f"❌ Error CRÍTICO obteniendo UUIDs: {e}")
            return None 
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def update_device_note(uuid: str, note: str):
        query = "UPDATE inspector.inspector SET strnote = $1, dtmodificationdate = NOW() WHERE uuidinspector = $2"
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, note, uuid)
            return True
        except Exception as e:
            logger.error(f"❌ Error DB update note: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def get_device_by_uuid(uuid: str) -> Dict[str, Any]:
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
        query = """
            SELECT 
                idInspectorHistory as id,
                uuidInspector as uuid,
                idTransactionStatus as status_id,
                boolOnline as is_online,
                intHistoryMemoryUsageMB as memory_usage,
                intHistoryMemoryTotalMB as memory_total,
                intHistoryStorageUsageMB as storage_usage,
                intHistoryStorageTotalMB as storage_total,
                intHistoryCpuTempC as cpu_temp,
                intHistoryCpuUsagePercent as cpu_usage,
                idHistoricScript as script_id,
                dtValidate as timestamp
            FROM inspector.StatusInspectorHistory
            WHERE uuidInspector = $1
              AND dtValidate BETWEEN $2 AND $3
            ORDER BY dtValidate ASC
        """
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query, uuid, start_date, end_date)
            return [dict(r) for r in records]
        except Exception as e:
            logger.error(f"❌ Error fetching history for {uuid}: {e}")
            return []
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def get_device_detail_full(uuid: str):
        # NOTA: Aquí deberías agregar el LEFT JOIN a DeviceStatus si quieres ver el nombre del estado nuevo
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
                data = dict(record)
                if isinstance(data.get('jsonbobservaciones'), str):
                     import json
                     data['jsonbobservaciones'] = json.loads(data['jsonbobservaciones'])
                
                if data.get('dtlastconnectivityevent'):
                    data['dtlastconnectivityevent'] = data['dtlastconnectivityevent'].replace(tzinfo=None)
                
                return data
            return None
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def update_device_fleet(uuid: str, new_fleet_slug: str):
        query = """
            UPDATE inspector.Inspector 
            SET stridInspectorFleet = $1, 
                dtModificationDate = NOW() 
            WHERE uuidInspector = $2
        """
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, new_fleet_slug, uuid)
            return True
        except Exception as e:
            logger.error(f"❌ Error DB update fleet: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def get_variables_dict(uuid: str) -> dict:
        query = """
            SELECT strDeviceVarName, strDeviceVarValue 
            FROM inspector.InspectorDeviceVariables
            WHERE uuidInspector = $1
        """
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query, uuid)
            return {r['strdevicevarname']: r['strdevicevarvalue'] for r in records}
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def upsert_variable(uuid: str, name: str, value: str):
        query_update = """
            UPDATE inspector.InspectorDeviceVariables 
            SET strDeviceVarValue = $3, dtModificationDate = NOW()
            WHERE uuidInspector = $1 AND strDeviceVarName = $2
        """
        query_insert = """
            INSERT INTO inspector.InspectorDeviceVariables (uuidInspector, strDeviceVarName, strDeviceVarValue)
            VALUES ($1, $2, $3)
        """
        conn = await PostgresConnector.get_connection()
        try:
            result = await conn.execute(query_update, uuid, name, value)
            if result == "UPDATE 0": 
                await conn.execute(query_insert, uuid, name, value)
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def delete_variable(uuid: str, name: str):
        query = "DELETE FROM inspector.InspectorDeviceVariables WHERE uuidInspector = $1 AND strDeviceVarName = $2"
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, uuid, name)
        finally:
            await PostgresConnector.release_connection(conn)