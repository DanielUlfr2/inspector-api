from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from typing import List
from src.repositories.history_repo import HistoryRepository
from src.api.v1.schemas.history_schema import GlobalStatsResponse

router = APIRouter()

@router.get("/global-stats", response_model=List[GlobalStatsResponse])
async def get_global_stats(
    start_date: datetime = Query(..., description="Fecha inicio (ISO 8601)"),
    end_date: datetime = Query(..., description="Fecha fin (ISO 8601)")
):
    """
    Retorna la evolución histórica de estados (Online, Offline, Free, Reduced).
    Ideal para graficar líneas de tiempo.
    """
    stats = await HistoryRepository.get_global_stats_range(start_date, end_date)
    
    if not stats:
        return []
        
    return stats