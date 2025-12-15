import logging
from databases.postgres_connector import PostgresConnector
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DeviceVarsRepository:
    
    @staticmethod
    async def upsert_batch(vars_data: List[Dict[str, Any]]):
        """
        Recibe una lista de diccionarios con: uuid, name, value
        """
        if not vars_data: return

        query = """
            INSERT INTO inspector.inspectordevicevariables (
                uuidinspector, strdevicevarname, strdevicevarvalue, 
                dtcreate, dtmodificationdate
            ) VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (uuidinspector, strdevicevarname) 
            DO UPDATE SET 
                strdevicevarvalue = EXCLUDED.strdevicevarvalue,
                dtmodificationdate = NOW();
        """
        
        values = []
        for v in vars_data:
            values.append((
                v["uuid"], 
                v["name"], 
                str(v["value"])
            ))
        
        conn = await PostgresConnector.get_connection()
        try:
            await conn.executemany(query, values)
        except Exception as e:
            logger.error(f"❌ Error guardando variables de dispositivo: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)