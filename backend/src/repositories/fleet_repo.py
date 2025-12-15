import logging
from databases.postgres_connector import PostgresConnector
from src.core.security import SecurityValidator
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class FleetRepository:
    
    @staticmethod
    async def upsert_batch(fleets_data: List[Dict[str, Any]]):
        if not fleets_data:
            logger.info("📭 No hay flotas para sincronizar.")
            return

        # 1. Validación de Seguridad
        safe_fleets = [SecurityValidator.sanitize_input(f) for f in fleets_data]

        # CAMBIO: Todo en minúsculas y sin comillas dobles en nombres de tablas/columnas
        query = """
            INSERT INTO inspector.inspectorfleets (
                stridinspectorfleet, strslug, strdevicetype, 
                intdevicecount, dtcreate, dtmodificationdate
            ) VALUES ($1, $2, $3, $4, NOW(), NOW())
            ON CONFLICT (stridinspectorfleet) 
            DO UPDATE SET 
                strslug = EXCLUDED.strslug,
                strdevicetype = EXCLUDED.strdevicetype,
                intdevicecount = EXCLUDED.intdevicecount,
                dtmodificationdate = NOW();
        """
        
        values = [
            (f["id"], f["slug"], f["device_type"], f.get("device_count", 0)) 
            for f in safe_fleets
        ]

        conn = await PostgresConnector.get_connection()
        try:
            await conn.executemany(query, values)
            logger.info(f"✅ {len(values)} flotas sincronizadas en DB.")
        except Exception as e:
            logger.error(f"❌ Error crítico insertando flotas: {e}")
            raise e 
        finally:
            await PostgresConnector.release_connection(conn)
    
    @staticmethod
    async def get_all_ids():
        """
        Retorna un SET con los IDs de flotas existentes.
        SEGURIDAD: Retorna None si falla para evitar loops.
        """
        query = 'SELECT stridinspectorfleet FROM inspector.inspectorfleets;'
        
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            return {r["stridinspectorfleet"] for r in records}
        except Exception as e:
            logger.error(f"❌ Error obteniendo IDs de flotas: {e}")
            return None # Importante: None, no set()
        finally:
            await PostgresConnector.release_connection(conn)