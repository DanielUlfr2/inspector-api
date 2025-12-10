import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="WireGuard Control API", version="1.0.0")

# --- CONFIGURACIÓN ---
# Leemos las variables que Docker inyecta desde vpn/.env
WG_HOST = os.getenv("WG_EASY_HOST", "wg-easy")
WG_PORT = os.getenv("WG_EASY_PORT", "51821")
WG_PASSWORD = os.getenv("WG_EASY_PASSWORD", "")
BASE_URL = f"http://{WG_HOST}:{WG_PORT}"

# Sesión persistente para mantener las cookies de autenticación
session = requests.Session()

def login_to_wg_easy():
    """Se autentica contra el servicio wg-easy para obtener la cookie de sesión"""
    try:
        payload = {"password": WG_PASSWORD}
        response = session.post(f"{BASE_URL}/api/session", json=payload, timeout=5)
        if response.status_code == 204:
            print("✅ Autenticado correctamente con WG-Easy")
            return True
        else:
            print(f"❌ Fallo de autenticación con WG-Easy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando a WG-Easy: {str(e)}")
        return False

# --- EVENTOS ---
@app.on_event("startup")
async def startup_event():
    print(f"🔌 Conectando a WG-Easy en {BASE_URL}...")
    login_to_wg_easy()

# --- RUTAS ---
@app.get("/")
def root():
    return {"service": "WireGuard Control API", "status": "running"}

@app.get("/health")
def health_check():
    """Verifica si podemos ver la API de wg-easy"""
    try:
        # Intentamos obtener la sesión o info básica
        resp = session.get(f"{BASE_URL}/api/session", timeout=3)
        if resp.status_code == 200:
            return {"status": "ok", "upstream": "connected"}
        # Si falla, intentamos reloguear
        if login_to_wg_easy():
            return {"status": "ok", "upstream": "reconnected"}
        return {"status": "error", "upstream": "unauthorized"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"WG-Easy unreachable: {str(e)}")

@app.get("/clients")
def get_clients():
    """Obtiene la lista de clientes VPN conectados"""
    try:
        response = session.get(f"{BASE_URL}/api/wireguard/client")
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            # Token expirado, reintentar login
            if login_to_wg_easy():
                return session.get(f"{BASE_URL}/api/wireguard/client").json()
            raise HTTPException(status_code=401, detail="Unauthorized from WG-Easy")
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching clients")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))