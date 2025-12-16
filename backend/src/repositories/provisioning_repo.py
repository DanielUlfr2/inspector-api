import logging
from databases.postgres_connector import PostgresConnector
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest

logger = logging.getLogger(__name__)

class ProvisioningRepository:

    @staticmethod
    async def create_service_and_link_device(uuid: str, data: ProvisioningRequest):
        """
        1. Inserta el InspectorService.
        2. Actualiza el Inspector vinculándolo al servicio.
        """
        conn = await PostgresConnector.get_connection()
        try:
            # Iniciamos transacción
            async with conn.transaction():
                
                # 1. INSERTAR SERVICIO
                # Usamos ON CONFLICT para actualizar si el servicio ya existía
                query_service = """
                    INSERT INTO inspector.inspectorservice (
                        strinspectorserviceid, idcity, idcmtsolt, idproduct, 
                        idtechnology, idservicetype, idcrm, straddress, 
                        strclientname, intdownspeed, intupspeed, dtmodificationdate
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW())
                    ON CONFLICT (strinspectorserviceid) DO UPDATE SET
                        idcity = EXCLUDED.idcity,
                        idcmtsolt = EXCLUDED.idcmtsolt,
                        straddress = EXCLUDED.straddress,
                        strclientname = EXCLUDED.strclientname,
                        intdownspeed = EXCLUDED.intdownspeed,
                        intupspeed = EXCLUDED.intupspeed,
                        dtmodificationdate = NOW();
                """
                await conn.execute(query_service,
                    data.inspector_service_id, # $1
                    data.city_id,              # $2
                    data.cmts_olt_id,          # $3
                    data.product_id,           # $4
                    data.technology_id,        # $5
                    data.service_type_id,      # $6
                    data.crm_id,               # $7
                    data.address,              # $8
                    data.client_name,          # $9
                    data.down_speed,           # $10
                    data.up_speed              # $11
                )

                # 2. ACTUALIZAR INSPECTOR (Vincular)
                query_inspector = """
                    UPDATE inspector.inspector
                    SET 
                        strinspectorname = $1,
                        strinspectorserviceid = $2,
                        idinventoryinspectorstatus = $3,
                        dtmodificationdate = NOW()
                    WHERE uuidinspector = $4;
                """
                await conn.execute(query_inspector,
                    data.new_device_name,      # $1
                    data.inspector_service_id, # $2 (FK al servicio creado arriba)
                    data.status_id,            # $3
                    uuid                       # $4
                )
                
                logger.info(f"✅ BD Provisioning exitoso para UUID: {uuid}")
                return True

        except Exception as e:
            logger.error(f"❌ Error DB Provisioning (Rollback): {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)