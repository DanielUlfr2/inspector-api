import logging
from src.services.balena_service import BalenaService
from src.repositories.fleet_repo import FleetRepository
from src.api.v1.schemas.fleet_schema import FleetCreateRequest

logger = logging.getLogger(__name__)

class FleetAdminService:

    # --- CREAR FLOTA ---
    @classmethod
    async def create_fleet(cls, data: FleetCreateRequest):
        logger.info(f"🚀 Creando flota: {data.name}")
        
        # 1. Traducir ID a Slug de Balena
        real_slug = await FleetRepository.get_device_type_slug_by_id(data.device_type_id)
        if not real_slug:
            return {"success": False, "message": "ID de tipo de dispositivo no válido."}

        if not BalenaService.login(): return {"success": False, "message": "Fallo Login Balena"}

        # 2. Crear en Balena
        fleet_data = BalenaService.create_fleet(data.name, real_slug, data.organization)
        if not fleet_data:
            return {"success": False, "message": "Error creando en Balena Cloud"}

        # 3. Guardar en BD Local
        fleet_to_save = {
            "id": fleet_data.get("app_name"),
            "slug": fleet_data.get("slug"),
            "device_type_id": data.device_type_id, # Guardamos el ID entero
            "device_count": 0
        }
        try:
            await FleetRepository.upsert_batch([fleet_to_save])
            return {"success": True, "message": "Flota creada exitosamente", "data": fleet_to_save}
        except Exception as e:
            return {"success": False, "message": f"Creada en Nube, pero falló BD: {e}"}

    # --- RENOMBRAR FLOTA ---
    @classmethod
    async def rename_fleet(cls, old_name: str, new_name: str):
        logger.info(f"✏️ Renombrando: {old_name} -> {new_name}")
        if not BalenaService.login(): return {"success": False, "message": "Fallo Login"}

        if BalenaService.rename_fleet(old_name, new_name):
            # Obtener el nuevo slug
            new_info = BalenaService.get_fleet_detail(new_name)
            new_slug = new_info.get("slug") if new_info else f"admin/{new_name}"

            try:
                await FleetRepository.rename_fleet_in_db(old_name, new_name, new_slug)
                return {"success": True, "message": "Flota renombrada correctamente"}
            except Exception as e:
                return {"success": False, "message": f"Renombrada en Nube, falló BD: {e}"}
        
        return {"success": False, "message": "Balena rechazó el renombrado"}

    # --- ELIMINAR FLOTA (CON REGLA ESTRICTA) ---
    @classmethod
    async def delete_fleet(cls, fleet_name: str):
        logger.info(f"🔥 Intentando eliminar flota: {fleet_name}")

        # 1. EL GUARDIÁN: Verificar si tiene equipos en BD Local
        device_count = await FleetRepository.count_devices_in_fleet(fleet_name)
        
        if device_count > 0:
            msg = f"⛔ ACCIÓN DENEGADA: La flota '{fleet_name}' tiene {device_count} equipos activos. Debe moverlos o eliminarlos primero."
            logger.warning(msg)
            return {"success": False, "message": msg, "error_code": "FLEET_NOT_EMPTY"}

        # 2. Si llegamos aquí, está vacía. Procedemos.
        if not BalenaService.login(): return {"success": False, "message": "Fallo Login"}

        # 3. Borrar en Balena
        if BalenaService.remove_fleet(fleet_name):
            try:
                # 4. Borrar en BD Local
                await FleetRepository.delete_fleet(fleet_name)
                return {"success": True, "message": "Flota vacía eliminada correctamente."}
            except Exception as e:
                return {"success": False, "message": f"Eliminada en Nube, error limpiando BD: {e}"}
        
        return {"success": False, "message": "Error eliminando en Balena (Verifique logs)"}