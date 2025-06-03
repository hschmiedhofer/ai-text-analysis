"""
Security module for API key authentication.

This module provides authentication functionality for the FastAPI application using
Bearer token authentication. It validates API keys from the Authorization header
against a configured environment variable.
"""

import os
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
# This should be set in your .env file as API_KEY=your_secret_key
API_KEY = os.getenv("API_KEY")

# Ensure API key is configured before starting the application
if not API_KEY:
    raise ValueError("No API_KEY found in environment variables.")

# Create HTTPBearer security scheme for extracting Bearer tokens from Authorization header
# This will automatically look for "Authorization: Bearer <token>" in request headers
security = HTTPBearer()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    """
    Verify API key from Authorization header.

    This function is used as a dependency in FastAPI routes to authenticate requests.
    It extracts the Bearer token from the Authorization header and compares it
    against the configured API_KEY environment variable.

    Args:
        credentials (HTTPAuthorizationCredentials): Automatically injected by FastAPI
            containing the Bearer token from the Authorization header.

    Returns:
        str: The validated API key if authentication succeeds.

    Raises:
        HTTPException: 401 Unauthorized if the provided API key doesn't match
            the configured API_KEY environment variable.
    """
    # Compare the provided token with the configured API key
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    # Return the validated API key
    return credentials.credentials
