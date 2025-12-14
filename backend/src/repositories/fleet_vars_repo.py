import logging
from databases.postgres_connector import PostgresConnector
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class FleetVarsRepository:
    @staticmethod
    async def upsert_batch(vars_data: List[Dict[str, Any]]):
        if not vars_data: return

        query = """
            INSERT INTO inspector.inspectorfleetsvariables (
                stridinspectorfleet, strfleetvarname, strfleetvarvalue, 
                dtcreate, dtmodificationdate
            ) VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (stridinspectorfleet, strfleetvarname) 
            DO UPDATE SET 
                strfleetvarvalue = EXCLUDED.strfleetvarvalue,
                dtmodificationdate = NOW();
        """
        values = [(v["fleet_slug"], v["name"], str(v["value"])) for v in vars_data]
        
        conn = await PostgresConnector.get_connection()
        try:
            await conn.executemany(query, values)
        except Exception as e:
            logger.error(f"❌ Error guardando variables de flota: {e}")
        finally:
            await PostgresConnector.release_connection(conn)