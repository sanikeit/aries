from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Union
from app.core.security import verify_token
from app.core.config import settings

# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# API Key header scheme
api_key_header = HTTPBearer(auto_error=False, scheme_name="API Key")

async def get_current_user_or_machine(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[HTTPAuthorizationCredentials] = Depends(api_key_header)
) -> dict:
    """
    Combined authentication dependency that tries JWT token first, then API key.
    This supports both user authentication and machine-to-machine authentication.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"get_current_user_or_machine called with token: {token[:20] if token else None}, api_key: {api_key.credentials[:20] if api_key else None}")
    
    # Try JWT token authentication first
    if token:
        logger.info("Attempting JWT token authentication")
        payload = verify_token(token)
        if payload:
            logger.info(f"JWT authentication successful for user: {payload.get('sub')}")
            return {"type": "user", "username": payload.get("sub"), "payload": payload}
        else:
            logger.error("JWT token verification failed")
    
    # Try API key authentication
    if api_key:
        logger.info("Attempting API key authentication")
        # In a real implementation, you would validate the API key against a database
        # For now, we'll use a simple validation
        if api_key.credentials and len(api_key.credentials) > 20:
            logger.info("API key authentication successful")
            return {"type": "machine", "api_key": api_key.credentials}
        else:
            logger.error("API key validation failed")
    
    # Both authentication methods failed
    logger.error("Both JWT and API key authentication failed")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_active_user(
    current_user: dict = Depends(get_current_user_or_machine)
) -> dict:
    """Get current active user (JWT authenticated)"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"get_current_active_user called with: {current_user}")
    
    if current_user["type"] != "user":
        logger.error(f"Authentication failed - user type is {current_user['type']}, expected 'user'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User authentication required"
        )
    logger.info(f"Authentication successful for user: {current_user.get('username')}")
    return current_user

async def get_current_machine(
    current_machine: dict = Depends(get_current_user_or_machine)
) -> dict:
    """Get current machine (API key authenticated)"""
    if current_machine["type"] != "machine":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key authentication required"
        )
    return current_machine