from src.repositories.catalogs_repo import CatalogsRepository

class CatalogsService:

    @classmethod
    async def get_initial_form_data(cls):
        """
        Retorna TODOS los catálogos en una sola petición.
        El frontend usará las IDs foráneas para filtrar en cascada.
        """
        return {
            # --- Ubicación (Cascada: Country -> Region -> Dept -> City) ---
            "countries": await CatalogsRepository.get_countries(),
            "regions": await CatalogsRepository.get_regions(),
            "departments": await CatalogsRepository.get_departments(),
            "cities": await CatalogsRepository.get_cities(),
            
            # --- Infraestructura ---
            "cmts_olts": await CatalogsRepository.get_all_cmts_olts(), # Filtrable por City

            # --- Hardware (Cascada: Brand + Type -> Reference) ---
            "terminal_types": await CatalogsRepository.get_terminal_types(),
            "terminal_brands": await CatalogsRepository.get_terminal_brands(),
            "terminal_references": await CatalogsRepository.get_all_terminal_references(),

            # --- Negocio (Selects simples) ---
            "products": await CatalogsRepository.get_products(),
            "technologies": await CatalogsRepository.get_technologies(),
            "service_types": await CatalogsRepository.get_service_types(),
            "crms": await CatalogsRepository.get_crms(),
            "statuses": await CatalogsRepository.get_inventory_statuses()
        }