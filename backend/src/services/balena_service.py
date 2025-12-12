import subprocess
import json
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class BalenaService:
    
    @staticmethod
    def login() -> bool:
        """Ejecuta 'balena login' usando las credenciales del .env"""
        try:
            print("🔐 Iniciando sesión en Balena CLI...")
            # Usamos --credentials para no pedir input interactivo
            cmd = [
                "balena", "login", 
                "--credentials", 
                "--email", settings.BALENA_EMAIL, 
                "--password", settings.BALENA_PASSWORD
            ]
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Login Balena exitoso")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error Login Balena: {e.stderr}")
            return False

    @staticmethod
    def get_fleets() -> list:
        """Ejecuta 'balena fleet list' y retorna JSON"""
        try:
            print("📡 Consultando Flotas...")
            result = subprocess.run(
                ["balena", "fleet", "list", "--json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            print(f"❌ Error obteniendo flotas: {e}")
            return []

    @staticmethod
    def get_devices_by_fleet(fleet_slug: str) -> list:
        """Ejecuta 'balena device list' por flota"""
        try:
            # print(f"🔍 Consultando dispositivos de: {fleet_slug}")
            result = subprocess.run(
                ["balena", "device", "list", "--fleet", fleet_slug, "--json"],
                capture_output=True, text=True, check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            print(f"⚠️ Error en flota {fleet_slug}: {e}")
            return []