from fastapi import APIRouter
from mock_data import generate_mock_resource_data

router = APIRouter(prefix="/api", tags=["resources"])

@router.get("/ships/{ship_symbol}/resources")
async def get_ship_resources(ship_symbol: str):
    """Get resource data for a specific ship"""
    return generate_mock_resource_data(ship_symbol)

@router.post("/ships/{ship_symbol}/resources/{action}")
async def execute_resource_action(ship_symbol: str, action: str, parameters: dict = {}):
    """Execute a resource management action on a ship"""
    action_responses = {
        "optimize-fuel": {"status": "success", "message": "Fuel optimization enabled", "efficiency_increase": 5},
        "refuel": {"status": "success", "message": "Ship refueled", "fuel_added": 50},
        "balance-power": {"status": "success", "message": f"Power balanced to {parameters.get('mode', 'normal')} mode"},
        "emergency-cooling": {"status": "success", "message": "Emergency cooling engaged", "temperature_reduction": 20}
    }
    
    return action_responses.get(action, {"status": "unknown", "message": f"Unknown action: {action}"})