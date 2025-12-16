import logging
from src.services.balena_service import BalenaService
from src.repositories.provisioning_repo import ProvisioningRepository
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest

logger = logging.getLogger(__name__)

class DeviceAdminService:

    @classmethod
    async def provision_device(cls, uuid: str, data: ProvisioningRequest):
        """
        Flujo Completo:
        1. Renombrar en Balena (Nube).
        2. Guardar en PostgreSQL (Local).
        """
        logger.info(f"🚀 Iniciando Provisioning para {uuid}...")

        # A. Login Balena
        if not BalenaService.login():
            return {"success": False, "message": "Fallo Login Balena"}

        # B. Renombrar en Balena
        # Hacemos esto primero porque depende de la red externa
        rename_ok = BalenaService.rename_device(uuid, data.new_device_name)
        if not rename_ok:
            return {"success": False, "message": "Error al renombrar en Balena Cloud. Revise conexión."}

        # C. Guardar en Base de Datos
        try:
            await ProvisioningRepository.create_service_and_link_device(uuid, data)
        except Exception as e:
            logger.error(f"⚠️ Desincronización: Balena renombró OK, pero BD falló: {e}")
            return {"success": False, "message": f"Error guardando en BD: {str(e)}"}

        return {"success": True, "message": "Dispositivo aprovisionado correctamente."}