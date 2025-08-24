from fastapi import APIRouter, HTTPException, Depends
import httpx

from ..models import HireCrewRequest
from ..config import HAS_VALID_TOKEN, SPACETRADERS_API_URL, SPACETRADERS_TOKEN
from ..mock_data import MOCK_AVAILABLE_CREW
from ..utilities import get_httpx_client

router = APIRouter(prefix="/api", tags=["crew"])

@router.get("/ships/{ship_symbol}/crew")
async def get_ship_crew(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get crew members for a specific ship"""
    if not HAS_VALID_TOKEN:
        # Return mock crew data
        return {
            "data": [
                {
                    "symbol": "CREW_001",
                    "name": "Captain Rodriguez",
                    "role": "PILOT",
                    "level": 5,
                    "experience": 850,
                    "health": 100,
                    "morale": 85,
                    "skills": {"piloting": 95, "navigation": 90, "leadership": 80},
                    "salary": 200
                },
                {
                    "symbol": "CREW_002", 
                    "name": "Engineer Smith",
                    "role": "ENGINEER",
                    "level": 4,
                    "experience": 640,
                    "health": 100,
                    "morale": 90,
                    "skills": {"engineering": 85, "repair": 80, "electronics": 75},
                    "salary": 150
                }
            ]
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/crew", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            # SpaceTraders might not have crew endpoints yet, return mock data
            return {
                "data": [
                    {
                        "symbol": "CREW_001",
                        "name": "Captain Rodriguez", 
                        "role": "PILOT",
                        "level": 5,
                        "experience": 850,
                        "health": 100,
                        "morale": 85,
                        "skills": {"piloting": 95, "navigation": 90, "leadership": 80},
                        "salary": 200
                    }
                ]
            }
    except Exception as e:
        # Return mock data if API fails
        return {
            "data": [
                {
                    "symbol": "CREW_001",
                    "name": "Captain Rodriguez",
                    "role": "PILOT", 
                    "level": 5,
                    "experience": 850,
                    "health": 100,
                    "morale": 85,
                    "skills": {"piloting": 95, "navigation": 90, "leadership": 80},
                    "salary": 200
                }
            ]
        }

@router.post("/ships/{ship_symbol}/crew/hire")
async def hire_crew_member(ship_symbol: str, request: HireCrewRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Hire a crew member for a ship"""
    if not HAS_VALID_TOKEN:
        # Mock hiring response
        hired_crew = next((crew for crew in MOCK_AVAILABLE_CREW if crew["id"] == request.hireableCrewId), None)
        if not hired_crew:
            raise HTTPException(status_code=404, detail="Crew member not found")
        
        return {
            "data": {
                "agent": {"credits": 999800},  # Deduct hiring cost
                "crew": {
                    "symbol": f"CREW_{len(MOCK_AVAILABLE_CREW) + 1:03d}",
                    "name": hired_crew["name"],
                    "role": hired_crew["role"],
                    "level": hired_crew["level"],
                    "experience": 0,
                    "health": 100,
                    "morale": 80,
                    "skills": hired_crew["skills"],
                    "salary": hired_crew["salary"]
                },
                "transaction": {
                    "waypointSymbol": "X1-DF55-20250X",
                    "shipSymbol": ship_symbol,
                    "totalPrice": 200,
                    "timestamp": "2023-11-01T00:00:00.000Z"
                }
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {"hireableCrewId": request.hireableCrewId}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/crew/hire", 
                                   json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/crew/available")
async def get_available_crew(waypoint_symbol: str = "X1-DF55-20250X", client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get available crew members for hire at a waypoint"""
    if not HAS_VALID_TOKEN:
        return {"data": MOCK_AVAILABLE_CREW}
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/systems/{waypoint_symbol}/crew", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            # If endpoint doesn't exist, return mock data
            return {"data": MOCK_AVAILABLE_CREW}
    except Exception as e:
        # Return mock data if API fails
        return {"data": MOCK_AVAILABLE_CREW}

@router.post("/ships/{ship_symbol}/crew/{crew_symbol}/dismiss")
async def dismiss_crew_member(ship_symbol: str, crew_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Dismiss a crew member from a ship"""
    if not HAS_VALID_TOKEN:
        return {
            "data": {
                "agent": {"credits": 999900},  # Partial refund
                "message": f"Crew member {crew_symbol} dismissed from {ship_symbol}"
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/crew/{crew_symbol}/dismiss", 
                                   headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))