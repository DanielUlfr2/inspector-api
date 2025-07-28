from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from app.db.connection import get_async_session
from app.db.models import Registro
from app.services.deps import require_admin
import pandas as pd
from fastapi.responses import StreamingResponse
from io import BytesIO
import logging

router = APIRouter()

# Configuración básica del logger
logger = logging.getLogger(__name__)

@router.get("/export_excel", summary="Exportar registros a archivo CSV")
async def export_csv(
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    try:
        result = await session.execute(select(Registro))
        registros = result.scalars().all()

        if not registros:
            logger.info("No hay registros para exportar.")
            return StreamingResponse(BytesIO(), media_type="text/csv")

        df = pd.DataFrame([r.as_dict() for r in registros])

        # Eliminar columna 'velocidad' si por algún motivo aún aparece
        if "velocidad" in df.columns:
            df.drop(columns=["velocidad"], inplace=True)

        # Renombrar columnas para exportar con nombres visibles
        column_labels = {
            "numero_inspector": "Número de inspector",
            "nombre": "Nombre",
            "observaciones": "Observaciones",
            "status": "Status",
            "region": "Región",
            "flota": "Flota",
            "encargado": "Encargado",
            "celular": "Celular",
            "correo": "Correo",
            "direccion": "Dirección",
            "uso": "Uso",
            "departamento": "Departamento",
            "ciudad": "Ciudad",
            "tecnologia": "Tecnología",
            "cmts_olt": "CMTS/OLT",
            "id_servicio": "ID Servicio",
            "mac_sn": "MAC/SN"
        }

        df.rename(columns=column_labels, inplace=True)

        output = BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)

        logger.info(f"Exportando {len(registros)} registros a CSV.")
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=registros_exportados.csv"}
        )
    except HTTPException:
        raise
    except SQLAlchemyError as se:
        logger.error(f"Error de base de datos al exportar: {se}")
        raise HTTPException(status_code=500, detail="Error de base de datos al exportar registros a CSV")
    except Exception as e:
        logger.error(f"Error inesperado al exportar registros a CSV: {e}")
        raise HTTPException(status_code=500, detail="Error interno al exportar registros a CSV")