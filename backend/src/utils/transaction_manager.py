import logging
from datetime import datetime
from databases.postgres_connector import PostgresConnector
from src.core.security import SecurityValidator

logger = logging.getLogger(__name__)

class TransactionStatus:
    SIN_INICIAR = 1
    EN_PROGRESO = 2
    FALLIDO = 3
    COMPLETO = 4
    CANCELADO = 5

class ScriptIds:
    # IDs quemados de scripts en base de datos.
    AUTO_RESTART = 'AUTOMATIC_RESTART_INSPECTOR'
    MANUAL_RESTART = 'MANUAL_RESTART_INSPECTOR'
    MANUAL_SHUTDOWN = 'MANUAL_SHUTDOWN_INSPECTOR'
    MANUAL_REBOOT = 'MANUAL_REBOOT_INSPECTOR'
    AUTO_SYNC = 'AUTOMATIC_COLLECTION_DATA_INSPECTOR'
    MANUAL_SYNC = 'MANUAL_COLLECTION_DATA_INSPECTOR'
    MANUAL_RENAME = 'MANUAL_RENAME_INSPECTOR'
    MANUAL_MOVE_FLEET = 'MANUAL_MOVE_FLEET_INSPECTOR'
    MANUAL_SET_VAR = 'MANUAL_SET_VAR_INSPECTOR'
    AUTO_VARS_SYNC = 'AUTOMATIC_COLLECTION_VARS_INSPECTOR'
    MANUAL_VARS_SYNC = 'MANUAL_COLLECTION_VARS_INSPECTOR'
    
class TransactionManager:

    @staticmethod
    async def get_current_status(script_id: str) -> int:
        """
        Consulta el estado actual de un script en la base de datos.
        Retorna el ID del estado (ej: 2 = En Progreso).
        Si no existe, retorna None.
        """
        query = """
            SELECT idtransactionstatus 
            FROM inspector.scripttransaction 
            WHERE strscriptid = $1
        """
        conn = await PostgresConnector.get_connection()
        try:
            status = await conn.fetchval(query, script_id)
            return status
        except Exception as e:
            logger.error(f"❌ Error consultando estado de {script_id}: {e}")
            return None
        finally:
            await PostgresConnector.release_connection(conn)
            
    @staticmethod
    async def start_transaction(script_id: str) -> int:
        """
        1. Actualiza ScriptTransaction (Tabla de estado actual).
        2. Crea registro en HistoricScriptTransaction (Tabla de auditoría) con estado 'En Progreso'.
        3. Retorna el ID del histórico para vincular detalles hijos.
        """
        conn = await PostgresConnector.get_connection()
        try:
            # 1. Actualizar Maestro (Estado actual)
            update_query = """
                UPDATE inspector.scripttransaction
                SET dtLastExecutionStart = NOW(),
                    idTransactionStatus = $1
                WHERE strscriptid = $2
            """
            await conn.execute(update_query, TransactionStatus.EN_PROGRESO, script_id)

            # 2. Insertar Histórico (Inicio)
            history_query = """
                INSERT INTO inspector.historicscripttransaction
                (strDescriptionFinish, dtExecutionStart, dtExecutionFinish, idTransactionStatus, strScriptId)
                VALUES ($1, NOW(), NOW(), $2, $3)
                RETURNING idHistoricScript
            """
            historic_id = await conn.fetchval(history_query, "Iniciando...", TransactionStatus.EN_PROGRESO, script_id)
            
            logger.info(f"🟢 Transacción iniciada: {script_id} (HistID: {historic_id})")
            return historic_id

        except Exception as e:
            logger.error(f"❌ Error iniciando transacción {script_id}: {e}")
            return None
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def finish_transaction(historic_id: int, script_id: str, status_id: int, description: str):
        """
        1. Actualiza el histórico (pone fecha fin y resultado).
        2. Actualiza el maestro ScriptTransaction (pone estado final).
        """
        if not historic_id: return

        clean_desc = description[:3000]

        conn = await PostgresConnector.get_connection()
        try:
            async with conn.transaction():
                # 1. Cerrar Histórico
                hist_query = """
                    UPDATE inspector.historicscripttransaction
                    SET dtExecutionFinish = NOW(),
                        idTransactionStatus = $1,
                        strDescriptionFinish = $2
                    WHERE idHistoricScript = $3
                """
                await conn.execute(hist_query, status_id, clean_desc, historic_id)

                # 2. Actualizar Maestro
                master_query = """
                    UPDATE inspector.scripttransaction
                    SET dtLastExecutionFinish = NOW(),
                        idTransactionStatus = $1
                    WHERE strscriptid = $2
                """
                await conn.execute(master_query, status_id, script_id)

            logger.info(f"🏁 Transacción finalizada: {script_id} - Estado: {status_id}")

        except Exception as e:
            logger.error(f"❌ Error finalizando transacción {script_id}: {e}")
        finally:
            await PostgresConnector.release_connection(conn)

