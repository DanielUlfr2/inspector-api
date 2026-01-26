from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from src.repositories.history_repo import HistoryRepository
from src.api.v1.schemas.history_schema import GlobalStatsResponse

router = APIRouter()

@router.get("/global-stats", response_model=List[GlobalStatsResponse])
async def get_global_stats(
    start_date: Optional[datetime] = Query(None, description="Fecha inicio (ISO 8601). Default: hace 7 días"),
    end_date: Optional[datetime] = Query(None, description="Fecha fin (ISO 8601). Default: ahora"),
    fleet_id: Optional[str] = Query(None, description="ID de la flota para filtrar (Opcional)")
):
    """
    Retorna la evolución histórica de estados (Online, Offline, Free, Reduced).
    Ideal para graficar líneas de tiempo.
    """
    # Asegurar que todas las fechas sean timezone-aware (UTC)
    if not end_date:
        end_date = datetime.now(timezone.utc)
    elif end_date.tzinfo is None:
        # Si viene sin timezone, asumimos UTC
        end_date = end_date.replace(tzinfo=timezone.utc)
    
    if not start_date:
        start_date = end_date - timedelta(days=7)
    elif start_date.tzinfo is None:
        # Si viene sin timezone, asumimos UTC
        start_date = start_date.replace(tzinfo=timezone.utc)

    stats = await HistoryRepository.get_global_stats_range(start_date, end_date, fleet_id)
    
    if not stats:
        return []
        
    return stats