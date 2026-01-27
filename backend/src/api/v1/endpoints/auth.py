"""
Authentication Endpoints
Modified: Client-side auth is used. These endpoints are reduced.
"""
from fastapi import APIRouter, HTTPException, Cookie
from typing import Optional
import logging

from src.services.keycloak_client import keycloak_client
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/user")
async def get_current_user(
    session_id: Optional[str] = Cookie(None, alias="SESSION_ID")
):
    """
    Get current user information from Keycloak
    
    This endpoint uses the access token (passed via cookie) to fetch user details.
    """
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    try:
        user_info = await keycloak_client.get_user_info(session_id)
        return user_info
        
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Failed to get user information. Token may be expired."
        )

# Callback, Refresh, and Session endpoints removed as they are handled client-side
