from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_inspectors():
    """
    Simula traer una lista de inspectores.
    Este endpoint será PROTEGIDO por KrakenD (solo usuarios con rol 'inspector').
    """
    return [
        {"uuid": "123-abc", "name": "Inspector Bogota Norte", "status": "online"},
        {"uuid": "456-def", "name": "Inspector Medellin Sur", "status": "offline"}
    ]