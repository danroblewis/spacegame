from fastapi import APIRouter
from mock_data import MOCK_AVAILABLE_CREW

router = APIRouter(prefix="/api", tags=["crew"])

@router.get("/crew/available")
async def get_available_crew(waypoint_symbol: str = "X1-DF55-20250X"):
    """Get available crew members for hire at a waypoint"""
    return {"data": MOCK_AVAILABLE_CREW}

@router.get("/ships/{ship_symbol}/crew")
async def get_ship_crew(ship_symbol: str):
    """Get crew members for a specific ship"""
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
            }
        ]
    }