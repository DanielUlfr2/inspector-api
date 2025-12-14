import subprocess
import json
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class BalenaService:
    
    @staticmethod
    def login() -> bool:
        # ... (Tu código de login actual) ...
        try:
            cmd = ["balena", "login", "--credentials", "--email", settings.BALENA_EMAIL, "--password", settings.BALENA_PASSWORD]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except Exception as e:
            logger.error(f"Error Login: {e}")
            return False

    @staticmethod
    def get_fleets() -> list:
        # ... (Tu código actual) ...
        try:
            result = subprocess.run(["balena", "fleet", "list", "--json"], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception:
            return []

    @staticmethod
    def get_devices_by_fleet(fleet_slug: str) -> list:
        # Este solo lo usamos para sacar los UUIDs
        try:
            result = subprocess.run(["balena", "device", "list", "--fleet", fleet_slug, "--json"], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception:
            return []

    # 👇 NUEVO MÉTODO: EL QUE TRAE LA DATA REAL
    @staticmethod
    def get_device_detail(uuid: str) -> dict:
        """Ejecuta 'balena device <UUID> --json' para obtener métricas reales"""
        try:
            # logger.debug(f"🔍 Consultando detalle profundo para UUID: {uuid}")
            result = subprocess.run(
                ["balena", "device", uuid, "--json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            logger.error(f"⚠️ Error obteniendo detalle de {uuid}: {e}")
            return {}
    
    @staticmethod
    def get_fleet_vars(fleet_slug: str) -> list:
        """Trae variables: balena env list --fleet <slug> --json"""
        try:
            result = subprocess.run(
                ["balena", "env", "list", "--fleet", fleet_slug, "--json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            # logger.warning(f"⚠️ No se pudieron traer variables de flota {fleet_slug}: {e}")
            return []

    @staticmethod
    def get_device_vars(uuid: str) -> list:
        """Trae variables: balena env list --device <uuid> --json"""
        try:
            result = subprocess.run(
                ["balena", "env", "list", "--device", uuid, "--json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except Exception:
            return []