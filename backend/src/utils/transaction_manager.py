import logging
from datetime import datetime
from databases.postgres_connector import PostgresConnector

logger = logging.getLogger(__name__)

class TransactionStatus:
    SIN_INICIAR = 1
    EN_PROGRESO = 2
    FALLIDO = 3
    COMPLETO = 4
    CANCELADO = 5

class ScriptIds:
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
    MANUAL_SET_NOTE = 'MANUAL_SET_NOTE_INSPECTOR'
    
class TransactionManager:

    @staticmethod
    async def get_current_status(script_id: str) -> int:
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
    async def start_transaction(script_id: str, user: str = "SYSTEM", role: str = "SYSTEM") -> int:
        """
        Inicia transacción guardando QUIÉN la ejecutó (user/role).
        """
        conn = await PostgresConnector.get_connection()
        try:
            # 1. Actualizar Maestro
            update_query = """
                UPDATE inspector.scripttransaction
                SET dtLastExecutionStart = NOW(),
                    idTransactionStatus = $1
                WHERE strscriptid = $2
            """
            await conn.execute(update_query, TransactionStatus.EN_PROGRESO, script_id)

            # 2. Insertar Histórico (CON USUARIO Y ROL)
            history_query = """
                INSERT INTO inspector.historicscripttransaction
                (strDescriptionFinish, dtExecutionStart, dtExecutionFinish, idTransactionStatus, strScriptId, strExecuterUser, strExecuterRole)
                VALUES ($1, NOW(), NOW(), $2, $3, $4, $5)
                RETURNING idHistoricScript
            """
            # Pasamos las 5 variables:
            historic_id = await conn.fetchval(history_query, "Iniciando...", TransactionStatus.EN_PROGRESO, script_id, user, role)
            
            logger.info(f"🟢 Transacción iniciada: {script_id} por {user} (HistID: {historic_id})")
            return historic_id

        except Exception as e:
            logger.error(f"❌ Error iniciando transacción {script_id}: {e}")
            return None
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def finish_transaction(historic_id: int, script_id: str, status_id: int, description: str):
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