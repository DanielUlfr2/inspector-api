"""
Authentication Endpoints
Handles OAuth2 flow with Keycloak and cookie-based session management
"""
from fastapi import APIRouter, HTTPException, Response, Cookie, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging

from src.services.keycloak_client import keycloak_client
from src.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class AuthCallbackRequest(BaseModel):
    """Request model for auth callback"""
    code: str
    redirect_uri: str


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh"""
    refresh_token: str


@router.post("/callback")
async def auth_callback(
    request: AuthCallbackRequest,
    response: Response
):
    """
    Handle OAuth2 callback from Keycloak
    
    This endpoint:
    1. Receives the authorization code from Keycloak
    2. Exchanges it for access and refresh tokens
    3. Sets secure HttpOnly cookies with the tokens
    4. Returns success response
    
    Security features:
    - HttpOnly: Prevents JavaScript access (XSS protection)
    - Secure: Only sent over HTTPS (in production)
    - SameSite: Prevents CSRF attacks
    """
    try:
        # Exchange authorization code for tokens
        tokens = await keycloak_client.exchange_code_for_tokens(
            code=request.code,
            redirect_uri=request.redirect_uri
        )
        
        # Extract tokens
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 300)  # Default 5 minutes
        
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="Failed to obtain access token from Keycloak"
            )
        
        # Set access token cookie (this is what KrakenD will validate)
        response.set_cookie(
            key="SESSION_ID",
            value=access_token,
            max_age=expires_in,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/"
        )
        
        # Set refresh token cookie (for token renewal)
        if refresh_token:
            response.set_cookie(
                key="REFRESH_TOKEN",
                value=refresh_token,
                max_age=settings.COOKIE_MAX_AGE * 24,  # Refresh tokens live longer
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                domain=settings.COOKIE_DOMAIN,
                path="/api/v1/auth"  # Only accessible to auth endpoints
            )
        
        logger.info("Successfully set authentication cookies")
        
        return {
            "success": True,
            "message": "Authentication successful",
            "expires_in": expires_in
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in auth callback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="REFRESH_TOKEN")
):
    """
    Refresh the access token using the refresh token
    
    This endpoint:
    1. Reads the refresh token from the HttpOnly cookie
    2. Requests a new access token from Keycloak
    3. Updates the SESSION_ID cookie with the new access token
    4. Optionally updates the refresh token if rotated
    """
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="No refresh token found. Please login again."
        )
    
    try:
        # Get new tokens from Keycloak
        tokens = await keycloak_client.refresh_access_token(refresh_token)
        
        access_token = tokens.get("access_token")
        new_refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in", 300)
        
        if not access_token:
            raise HTTPException(
                status_code=500,
                detail="Failed to refresh access token"
            )
        
        # Update access token cookie
        response.set_cookie(
            key="SESSION_ID",
            value=access_token,
            max_age=expires_in,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            domain=settings.COOKIE_DOMAIN,
            path="/"
        )
        
        # Update refresh token if rotated (Keycloak can rotate refresh tokens)
        if new_refresh_token and new_refresh_token != refresh_token:
            response.set_cookie(
                key="REFRESH_TOKEN",
                value=new_refresh_token,
                max_age=settings.COOKIE_MAX_AGE * 24,
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                domain=settings.COOKIE_DOMAIN,
                path="/api/v1/auth"
            )
        
        logger.info("Successfully refreshed access token")
        
        return {
            "success": True,
            "message": "Token refreshed successfully",
            "expires_in": expires_in
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Failed to refresh token. Please login again."
        )


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None, alias="REFRESH_TOKEN")
):
    """
    Logout user and clear authentication cookies
    
    This endpoint:
    1. Revokes the refresh token in Keycloak
    2. Clears all authentication cookies
    3. Returns success response
    """
    try:
        # Revoke token in Keycloak if available
        if refresh_token:
            await keycloak_client.logout(refresh_token)
        
        # Clear SESSION_ID cookie
        response.delete_cookie(
            key="SESSION_ID",
            path="/",
            domain=settings.COOKIE_DOMAIN
        )
        
        # Clear REFRESH_TOKEN cookie
        response.delete_cookie(
            key="REFRESH_TOKEN",
            path="/api/v1/auth",
            domain=settings.COOKIE_DOMAIN
        )
        
        logger.info("Successfully logged out user")
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        # Even if Keycloak logout fails, we still clear cookies
        response.delete_cookie(key="SESSION_ID", path="/", domain=settings.COOKIE_DOMAIN)
        response.delete_cookie(key="REFRESH_TOKEN", path="/api/v1/auth", domain=settings.COOKIE_DOMAIN)
        
        return {
            "success": True,
            "message": "Logged out (cookies cleared)"
        }


@router.get("/session")
async def check_session(
    session_id: Optional[str] = Cookie(None, alias="SESSION_ID")
):
    """
    Check if there's an active session
    
    This is a simple endpoint that the frontend can call to verify
    if the user has a valid session cookie.
    
    Note: This doesn't validate the JWT, it just checks if the cookie exists.
    KrakenD will handle JWT validation for protected endpoints.
    """
    if session_id:
        return {
            "authenticated": True,
            "message": "Active session found"
        }
    else:
        return {
            "authenticated": False,
            "message": "No active session"
        }


@router.get("/user")
async def get_current_user(
    session_id: Optional[str] = Cookie(None, alias="SESSION_ID")
):
    """
    Get current user information from Keycloak
    
    This endpoint uses the access token to fetch user details from Keycloak.
    Useful for displaying user profile information in the frontend.
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
