import httpx
from typing import AsyncGenerator

# HTTP client for SpaceTraders API
async def get_httpx_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Dependency that provides an HTTP client for SpaceTraders API calls"""
    async with httpx.AsyncClient() as client:
        yield client

# Global security status storage (in production, this would be in a database)
ship_security_status = {}