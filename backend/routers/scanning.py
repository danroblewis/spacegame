from fastapi import APIRouter
from mock_data import MOCK_SCAN_RESULTS, MOCK_SURVEYS

router = APIRouter(prefix="/api", tags=["scanning"])

@router.post("/ships/{ship_symbol}/scan/systems")
async def scan_systems(ship_symbol: str):
    """Long-range sensors - Detect systems and celestial objects"""
    return {
        "data": {
            "cooldown": {
                "shipSymbol": ship_symbol,
                "totalSeconds": 70,
                "remainingSeconds": 70,
                "expiration": "2023-11-01T00:01:10.000Z"
            },
            "systems": MOCK_SCAN_RESULTS["systems"]
        }
    }

@router.post("/ships/{ship_symbol}/survey")
async def create_survey(ship_symbol: str):
    """Resource mapping - Create detailed survey of current waypoint"""
    return {
        "data": {
            "cooldown": {
                "shipSymbol": ship_symbol,
                "totalSeconds": 60,
                "remainingSeconds": 60,
                "expiration": "2023-11-01T00:01:00.000Z"
            },
            "surveys": MOCK_SURVEYS
        }
    }