"""
Keycloak Client Service
Handles authentication flow with Keycloak for cookie-based authentication
"""
import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class KeycloakClient:
    """Client for interacting with Keycloak authentication server"""
    
    def __init__(self):
        self.server_url = settings.KEYCLOAK_URL
        self.realm = settings.KEYCLOAK_REALM
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self.client_secret = settings.KEYCLOAK_CLIENT_SECRET
        
        # Build base URLs
        self.realm_url = f"{self.server_url}/realms/{self.realm}"
        self.token_url = f"{self.realm_url}/protocol/openid-connect/token"
        self.logout_url = f"{self.realm_url}/protocol/openid-connect/logout"
        self.userinfo_url = f"{self.realm_url}/protocol/openid-connect/userinfo"
        
    async def exchange_code_for_tokens(
        self, 
        code: str, 
        redirect_uri: str
    ) -> Dict[str, any]:
        """
        Exchange authorization code for access and refresh tokens
        
        Args:
            code: Authorization code from Keycloak redirect
            redirect_uri: The redirect URI used in the initial auth request
            
        Returns:
            Dict containing access_token, refresh_token, expires_in, etc.
            
        Raises:
            httpx.HTTPStatusError: If token exchange fails
        """
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                tokens = response.json()
                
                logger.info(f"Successfully exchanged code for tokens")
                return tokens
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to exchange code for tokens: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token exchange: {str(e)}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, any]:
        """
        Refresh an access token using a refresh token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Dict containing new access_token, refresh_token, expires_in, etc.
            
        Raises:
            httpx.HTTPStatusError: If token refresh fails
        """
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                tokens = response.json()
                
                logger.info("Successfully refreshed access token")
                return tokens
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to refresh token: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {str(e)}")
            raise
    
    async def logout(self, refresh_token: str) -> bool:
        """
        Logout user by revoking the refresh token in Keycloak
        
        Args:
            refresh_token: The refresh token to revoke
            
        Returns:
            True if logout successful, False otherwise
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.logout_url,
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                
                logger.info("Successfully logged out user from Keycloak")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to logout from Keycloak: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during logout: {str(e)}")
            return False
    
    async def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Get user information from Keycloak using access token
        
        Args:
            access_token: Valid access token
            
        Returns:
            Dict containing user information
            
        Raises:
            httpx.HTTPStatusError: If request fails
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                user_info = response.json()
                
                logger.info(f"Successfully retrieved user info for user: {user_info.get('sub')}")
                return user_info
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get user info: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting user info: {str(e)}")
            raise


# Singleton instance
keycloak_client = KeycloakClient()
