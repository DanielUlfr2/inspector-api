"""
Authentication Endpoints
Modified: Client-side auth is used. These endpoints are reduced.
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import logging

from src.services.keycloak_client import keycloak_client
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/user")
async def get_current_user(
    x_user_id: str = Header(None, alias="X-User-Id"),
    x_role: str = Header(None, alias="X-Role")
):
    """
    Get current user information (propagated by Gateway)
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated (Missing X-User-Id)"
        )
    
    return {
        "sub": x_user_id,
        "roles": [x_role] if x_role else []
    }

from pydantic import BaseModel

class UserAvatarUpdate(BaseModel):
    avatar_id: str

@router.post("/avatar")
async def update_user_avatar(
    request: UserAvatarUpdate,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    authorization: Optional[str] = Header(None)
):
    """
    Update the user's avatar in Keycloak attributes.
    Supports both Gateway-injected headers AND direct Bearer token validation fallback.
    """
    user_id = x_user_id

    # Fallback: Validate Bearer Token if Gateway didn't inject ID
    if not user_id and authorization:
        try:
            scheme, token = authorization.split()
            if scheme.lower() == 'bearer':
                user_info = await keycloak_client.get_user_info(token)
                user_id = user_info.get("sub")
        except Exception as e:
            logger.warning(f"Fallback token validation failed: {str(e)}")
            pass

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    try:
        # Update Attribute in Keycloak using Admin Client
        await keycloak_client.update_user_attribute(
            user_id, 
            {"avatar": [request.avatar_id]}
        )
        
        return {"success": True, "message": "Avatar updated successfully", "avatar": request.avatar_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating avatar: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update avatar in identity provider."
        )
