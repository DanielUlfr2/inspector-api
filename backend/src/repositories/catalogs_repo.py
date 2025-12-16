import logging
from databases.postgres_connector import PostgresConnector

logger = logging.getLogger(__name__)

class CatalogsRepository:

    # ==========================================
    # 1. JERARQUÍA GEOGRÁFICA (El Árbol)
    # ==========================================

    @staticmethod
    async def get_countries():
        # Nivel 1
        query = "SELECT idcountry, strcountryname FROM inspector.country ORDER BY strcountryname ASC;"
        return await CatalogsRepository._fetch_simple(query)

    @staticmethod
    async def get_regions():
        # Nivel 2 (Traemos idcountry para que el frontend filtre)
        query = "SELECT idregion, strregionname, idcountry FROM inspector.region ORDER BY strregionname ASC;"
        return await CatalogsRepository._fetch_simple(query)

    @staticmethod
    async def get_departments():
        # Nivel 3 (Traemos idregion)
        query = "SELECT iddepartment, strdepartmentname, idregion FROM inspector.department ORDER BY strdepartmentname ASC;"
        return await CatalogsRepository._fetch_simple(query)

    @staticmethod
    async def get_cities():
        # Nivel 4 (Traemos iddepartment)
        query = "SELECT idcity, strcityname, iddepartment FROM inspector.city ORDER BY strcityname ASC;"
        return await CatalogsRepository._fetch_simple(query)

    # ==========================================
    # 2. INFRAESTRUCTURA (CMTS / OLT)
    # ==========================================
    
    @staticmethod
    async def get_all_cmts_olts():
        """
        Trae lista de OLTs/CMTS.
        Incluye 'idcity' para filtrar por ubicación.
        Incluye 'idterminalreference' por si necesitas filtrar por tipo técnico.
        """
        query = """
            SELECT 
                idcmtsolt, 
                strcmtsoltname, 
                idcity, 
                idterminalreference 
            FROM inspector.cmtsolt 
            ORDER BY strcmtsoltname ASC;
        """
        return await CatalogsRepository._fetch_simple(query)

    # ==========================================
    # 3. HARDWARE Y EQUIPOS (Terminales)
    # ==========================================

    @staticmethod
    async def get_terminal_types():
        # Ej: CMTS, OLT, ONT, Cablemodem
        query = "SELECT idterminaltype, strterminaltype FROM inspector.terminaltype ORDER BY strterminaltype ASC;"
        return await CatalogsRepository._fetch_simple(query)

    @staticmethod
    async def get_terminal_brands():
        # Ej: Huawei, Arris, ZTE
        query = "SELECT idterminalbrand, strterminalbrand FROM inspector.terminalbrand ORDER BY strterminalbrand ASC;"
        return await CatalogsRepository._fetch_simple(query)

    @staticmethod
    async def get_all_terminal_references():
        """
        Referencias (Modelos).
        Incluye Marca y Tipo para que el frontend filtre (Ej: Mostrar solo ONTs Huawei).
        """
        query = """
            SELECT 
                idterminalreference, 
                strterminalreference, 
                idterminalbrand, 
                idterminaltype 
            FROM inspector.terminalreference 
            ORDER BY strterminalreference ASC;
        """
        return await CatalogsRepository._fetch_simple(query)

    # ==========================================
    # 4. NEGOCIO Y GESTIÓN
    # ==========================================

    @staticmethod
    async def get_products():
        # Ej: BA, TOIP, TV
        query = "SELECT idproduct, strproductname FROM inspector.product ORDER BY strproductname ASC;"
        return await CatalogsRepository._fetch_simple(query)
    
    @staticmethod
    async def get_technologies():
        # Ej: GPON, HFC
        query = "SELECT idtechnology, strtechnologyname FROM inspector.technology ORDER BY strtechnologyname ASC;"
        return await CatalogsRepository._fetch_simple(query)

    @staticmethod
    async def get_service_types():
        # Ej: Default, Interno Tigo
        query = "SELECT idservicetype, strservicetypename FROM inspector.servicetype ORDER BY strservicetypename ASC;"
        return await CatalogsRepository._fetch_simple(query)
    
    @staticmethod
    async def get_crms():
        # Ej: Siebel
        query = "SELECT idcrm, strcrmname FROM inspector.crm ORDER BY strcrmname ASC;"
        return await CatalogsRepository._fetch_simple(query)

    @staticmethod
    async def get_inventory_statuses():
        # Ej: Ocupado, Libre
        query = "SELECT idinventoryinspectorstatus, strinventorystatus FROM inspector.inventoryinspectorstatus ORDER BY idinventoryinspectorstatus ASC;"
        return await CatalogsRepository._fetch_simple(query)

    # --- Helper Genérico ---
    @staticmethod
    async def _fetch_simple(query):
        conn = await PostgresConnector.get_connection()
        try:
            records = await conn.fetch(query)
            return [dict(r) for r in records]
        except Exception as e:
            logger.error(f"❌ Error en catálogo: {e}")
            return []
        finally:
            await PostgresConnector.release_connection(conn)