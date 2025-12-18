import logging
from typing import List, Dict, Any
from databases.postgres_connector import PostgresConnector
from src.core.security import SecurityValidator

logger = logging.getLogger(__name__)

class FleetRepository:
    
    # -------------------------------------------------------------------------
    # 1. SINCRONIZACIÓN (Escritura Masiva)
    # -------------------------------------------------------------------------
    @staticmethod
    async def upsert_batch(fleets_data: List[Dict[str, Any]]):
        if not fleets_data:
            logger.info("📭 No hay flotas para sincronizar.")
            return

        # 1. Validación de Seguridad
        safe_fleets = [SecurityValidator.sanitize_input(f) for f in fleets_data]

        query = """
            INSERT INTO inspector.InspectorFleets (
                stridInspectorFleet, 
                strSlug, 
                idDeviceType, 
                intDeviceCount, 
                dtCreate, 
                dtModificationDate
            ) VALUES ($1, $2, $3, $4, NOW(), NOW())
            ON CONFLICT (stridInspectorFleet) 
            DO UPDATE SET 
                strSlug = EXCLUDED.strSlug,
                idDeviceType = EXCLUDED.idDeviceType,
                intDeviceCount = EXCLUDED.intDeviceCount,
                dtModificationDate = NOW();
        """
        
        values = [
            (
                f["id"], 
                f["slug"], 
                f["device_type_id"], 
                f.get("device_count", 0)
            ) 
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
    
    # -------------------------------------------------------------------------
    # 2. LECTURA Y CACHÉ
    # -------------------------------------------------------------------------
    @staticmethod
    async def get_all_ids():
        query = 'SELECT stridinspectorfleet FROM inspector.inspectorfleets;'
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            return {r["stridinspectorfleet"] for r in records}
        except Exception as e:
            logger.error(f"❌ Error obteniendo IDs de flotas: {e}")
            return None 
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def get_device_type_map():
        query = "SELECT idDeviceType, strDeviceSlug FROM inspector.DeviceType;"
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            return {r['strdeviceslug']: r['iddevicetype'] for r in records}
        except Exception as e:
            logger.error(f"❌ Error obteniendo mapa de device types: {e}")
            return {}
        finally:
            await PostgresConnector.release_connection(conn)

    # -------------------------------------------------------------------------
    # 3. GESTIÓN ADMINISTRATIVA (CRUD + VALIDACIONES)
    # -------------------------------------------------------------------------

    # [NUEVO] El Guardián: Cuenta equipos antes de permitir borrar
    @staticmethod
    async def count_devices_in_fleet(fleet_id: str) -> int:
        """
        Consulta cuántos equipos existen asociados a esta flota.
        """
        query = "SELECT COUNT(*) FROM inspector.inspector WHERE stridinspectorfleet = $1"
        conn = await PostgresConnector.get_connection()
        try:
            return await conn.fetchval(query, fleet_id)
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def delete_fleet(fleet_id: str):
        """
        Elimina la flota. (El servicio ya debió verificar que count == 0)
        """
        query = "DELETE FROM inspector.inspectorfleets WHERE stridinspectorfleet = $1"
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, fleet_id)
            logger.info(f"✅ DB: Flota {fleet_id} eliminada.")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando flota en BD: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)

    # [MEJORA] Manejo de hijos al renombrar
    @staticmethod
    async def rename_fleet_in_db(old_id: str, new_id: str, new_slug: str):
        """
        Actualiza el nombre de la flota y mueve los equipos al nuevo nombre.
        Se hace en transacción para evitar errores de llave foránea.
        """
        # 1. Actualizar hijos (Equipos) para que apunten al nuevo ID
        # Nota: Esto es un truco. Si hay FK estricta sin cascade, puede requerir
        # desactivar constraints momentáneamente o crear el padre nuevo primero.
        # Asumiendo ON UPDATE CASCADE en la BD, solo actualizamos el padre.
        # Si NO tienes Cascade, descomenta la linea de children y ajústala según tu estrategia.
        
        query_parent = """
            UPDATE inspector.inspectorfleets
            SET stridinspectorfleet = $1, strslug = $2, dtmodificationdate = NOW()
            WHERE stridinspectorfleet = $3
        """
        
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query_parent, new_id, new_slug, old_id)
            logger.info(f"✅ DB: Flota renombrada {old_id} -> {new_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error renombrando flota en BD: {e}")
            raise e
        finally:
            await PostgresConnector.release_connection(conn)

    # --- HELPERS PARA DROPDOWNS ---
    @staticmethod
    async def get_all_device_types():
        query = "SELECT idDeviceType, strDeviceNameType, strDeviceSlug FROM inspector.DeviceType ORDER BY strDeviceNameType ASC;"
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            return [dict(r) for r in records]
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def get_device_type_slug_by_id(device_type_id: int):
        query = "SELECT strDeviceSlug FROM inspector.DeviceType WHERE idDeviceType = $1"
        conn = await PostgresConnector.get_connection()
        try:
            return await conn.fetchval(query, device_type_id)
        finally:
            await PostgresConnector.release_connection(conn)
    
    @staticmethod
    async def get_variables_dict(fleet_slug: str) -> dict:
        """
        Retorna un diccionario { 'NOMBRE_VAR': 'VALOR' } de la BD local.
        """
        query = """
            SELECT strFleetVarName, strFleetVarValue 
            FROM inspector.InspectorFleetsVariables
            WHERE stridInspectorFleet = $1
        """
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query, fleet_slug)
            return {r['strfleetvarname']: r['strfleetvarvalue'] for r in records}
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def upsert_variable(fleet_slug: str, name: str, value: str):
        """
        Inserta o Actualiza una variable de flota.
        """
        # Intentamos Update primero
        query_update = """
            UPDATE inspector.InspectorFleetsVariables 
            SET strFleetVarValue = $3, dtModificationDate = NOW()
            WHERE stridInspectorFleet = $1 AND strFleetVarName = $2
        """
        # Si no existe, Insert
        query_insert = """
            INSERT INTO inspector.InspectorFleetsVariables (stridInspectorFleet, strFleetVarName, strFleetVarValue)
            VALUES ($1, $2, $3)
        """
        
        conn = await PostgresConnector.get_connection()
        try:
            result = await conn.execute(query_update, fleet_slug, name, value)
            if result == "UPDATE 0": # Si no actualizó nada, insertamos
                await conn.execute(query_insert, fleet_slug, name, value)
        finally:
            await PostgresConnector.release_connection(conn)

    @staticmethod
    async def delete_variable(fleet_slug: str, name: str):
        """
        Elimina una variable de la BD local.
        """
        query = "DELETE FROM inspector.InspectorFleetsVariables WHERE stridInspectorFleet = $1 AND strFleetVarName = $2"
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, fleet_slug, name)
        finally:
            await PostgresConnector.release_connection(conn)