import logging
from databases.postgres_connector import PostgresConnector

logger = logging.getLogger(__name__)

class HistoryRepository:

    @staticmethod
    async def log_device_snapshot(historic_id: int, uuid: str, status_id: int, snapshot: dict):
        """
        Inserta el detalle técnico del equipo (Snapshot) vinculado a una transacción histórica existente.
        """
        if not snapshot: snapshot = {}

        query = """
            INSERT INTO inspector.StatusInspectorHistory (
                uuidInspector, 
                idTransactionStatus, 
                boolOnline, 
                intHistoryMemoryUsageMB, 
                intHistoryMemoryTotalMB,
                intHistoryStorageUsageMB, 
                intHistoryStorageTotalMB, 
                intHistoryCpuTempC, 
                intHistoryCpuUsagePercent, 
                idHistoricScript, 
                dtValidate
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW());
        """

        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(
                query,
                uuid,
                status_id,
                snapshot.get('is_online', False),
                snapshot.get('memory_usage', 0),
                snapshot.get('memory_total', 0),
                snapshot.get('storage_usage', 0),
                snapshot.get('storage_total', 0),
                snapshot.get('cpu_temp', 0),
                snapshot.get('cpu_usage', 0),
                historic_id # FK al padre que creó el TransactionManager
            )
        except Exception as e:
            logger.error(f"❌ Error guardando snapshot de historial: {e}")
        finally:
            await PostgresConnector.release_connection(conn)