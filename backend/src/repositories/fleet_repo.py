from typing import List, Optional
from databases.postgres_connector import PostgresConnector
from pydantic import BaseModel

# Modelo interno rápido para el repo
class FleetModel(BaseModel):
    stridInspectorFleet: str
    strSlug: str
    strDeviceType: str
    intDeviceCount: int = 0

class FleetRepository:
    @staticmethod
    async def upsert_fleet(fleet: FleetModel):
        """
        Inserta la flota si no existe, o actualiza si ya existe (Upsert)
        """
        query = """
            INSERT INTO inspector."InspectorFleets" 
            ("stridInspectorFleet", "strSlug", "strDeviceType", "intDeviceCount", "dtCreate", "dtModificationDate")
            VALUES ($1, $2, $3, $4, NOW(), NOW())
            ON CONFLICT ("stridInspectorFleet") 
            DO UPDATE SET 
                "strSlug" = EXCLUDED."strSlug",
                "intDeviceCount" = EXCLUDED."intDeviceCount",
                "dtModificationDate" = NOW();
        """
        conn = await PostgresConnector.get_connection()
        try:
            await conn.execute(query, fleet.stridInspectorFleet, fleet.strSlug, fleet.strDeviceType, fleet.intDeviceCount)
        finally:
            await PostgresConnector.release_connection(conn)