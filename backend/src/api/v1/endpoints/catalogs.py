from fastapi import APIRouter, HTTPException
from src.services.catalogs_service import CatalogsService

router = APIRouter()

@router.get("/form-options")
async def get_all_form_options():
    """
    Retorna el árbol completo de opciones para el formulario de aprovisionamiento.
    """
    try:
        return await CatalogsService.get_initial_form_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))