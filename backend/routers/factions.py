from fastapi import APIRouter, HTTPException, Depends
import httpx
from config import HAS_VALID_TOKEN, SPACETRADERS_API_URL, SPACETRADERS_TOKEN
from mock_data import MOCK_FACTIONS
from services import get_httpx_client

router = APIRouter(prefix="/api", tags=["factions"])

@router.get("/factions")
async def get_factions(client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get all factions"""
    if not HAS_VALID_TOKEN:
        return MOCK_FACTIONS
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/factions", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))