import subprocess
import json
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class BalenaService:
    
    # ==========================================
    # CÓDIGO EXISTENTE (Login, Getters, Vars)
    # ==========================================
    
    @staticmethod
    def login() -> bool:
        try:
            cmd = ["balena", "login", "--credentials", "--email", settings.BALENA_EMAIL, "--password", settings.BALENA_PASSWORD]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except Exception as e:
            logger.error(f"Error Login: {e}")
            return False

    @staticmethod
    def get_fleets() -> list:
        try:
            result = subprocess.run(["balena", "fleet", "list", "--json"], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception:
            return []

    @staticmethod
    def get_devices_by_fleet(fleet_slug: str) -> list:
        try:
            result = subprocess.run(["balena", "device", "list", "--fleet", fleet_slug, "--json"], capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception:
            return []

    @staticmethod
    def get_device_detail(uuid: str) -> dict:
        """Ejecuta 'balena device <UUID> --json' para obtener métricas reales"""
        try:
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
        try:
            result = subprocess.run(
                ["balena", "env", "list", "--fleet", fleet_slug, "--json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            return []

    @staticmethod
    def get_device_vars(uuid: str) -> list:
        try:
            result = subprocess.run(
                ["balena", "env", "list", "--device", uuid, "--json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except Exception:
            return []
    
    @staticmethod
    def set_fleet_variable(fleet_slug: str, key: str, value: str):
        try:
            clean_slug = fleet_slug.split('/')[-1] if '/' in fleet_slug else fleet_slug
            subprocess.run(
                ["balena", "env", "add", key, value, "--fleet", clean_slug],
                check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            return False

    @staticmethod
    def set_device_variable(uuid: str, key: str, value: str):
        try:
            subprocess.run(
                ["balena", "env", "add", key, value, "--device", uuid],
                check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            return False
    
    @staticmethod
    def rename_device(uuid: str, new_name: str) -> bool:
        try:
            logger.info(f"⚡ Ejecutando rename para {uuid} -> {new_name}")
            subprocess.run(
                ["balena", "device", "rename", uuid, new_name],
                check=True, capture_output=True, text=True
            )
            logger.info(f"✅ Balena rename exitoso.")
            return True
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.strip()
            logger.error(f"❌ Error Balena CLI rename: {err_msg}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado en rename: {e}")
            return False

    # ==========================================
    # 👇 NUEVOS MÉTODOS REQUERIDOS PARA ADMIN DE FLOTAS
    # ==========================================

    @staticmethod
    def get_fleet_detail(slug_or_name: str) -> dict:
        """Helper para traer info de una flota específica (Usado al crear)"""
        try:
            result = subprocess.run(
                ["balena", "fleet", slug_or_name, "--json"],
                check=True, capture_output=True, text=True
            )
            return json.loads(result.stdout)
        except Exception:
            return None

    @staticmethod
    def create_fleet(name: str, device_type: str, organization: str = None) -> dict:
        """
        Crea una flota en Balena.
        Comando: balena fleet create <name> --type <device_type>
        """
        try:
            cmd = ["balena", "fleet", "create", name, "--type", device_type]
            if organization:
                cmd.extend(["--organization", organization])

            logger.info(f"⚡ Creando flota en Balena: {name} ({device_type})")
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Retornamos el detalle de la flota recién creada
            return BalenaService.get_fleet_detail(name)

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error creando flota {name}: {e.stderr.strip()}")
            return None

    @staticmethod
    def rename_fleet(old_name: str, new_name: str) -> bool:
        """
        Comando: balena fleet rename <old> <new>
        """
        try:
            logger.info(f"✏️ Renombrando flota {old_name} -> {new_name}")
            subprocess.run(
                ["balena", "fleet", "rename", old_name, new_name],
                check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error rename fleet: {e.stderr.strip()}")
            return False

    @staticmethod
    def remove_fleet(fleet_name: str) -> bool:
        """
        Comando: balena fleet rm <name> --yes
        """
        try:
            logger.info(f"🗑️ Eliminando flota {fleet_name}...")
            # IMPORTANTE: --yes evita el prompt interactivo
            subprocess.run(
                ["balena", "fleet", "rm", fleet_name, "--yes"],
                check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error delete fleet: {e.stderr.strip()}")
            return False

    @staticmethod
    def move_device(uuid: str, target_fleet_slug: str) -> bool:
        """
        Mueve dispositivo entre flotas.
        Comando: balena device move <uuid> --fleet <target>
        """
        try:
            logger.info(f"🚚 Moviendo dispositivo {uuid} a flota {target_fleet_slug}...")
            subprocess.run(
                ["balena", "device", "move", uuid, "--fleet", target_fleet_slug],
                check=True, capture_output=True, text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error moviendo dispositivo: {e.stderr.strip()}")
            return False