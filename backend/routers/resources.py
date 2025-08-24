from fastapi import APIRouter, HTTPException, Depends
import httpx

from ..config import HAS_VALID_TOKEN
from ..mock_data import generate_mock_resource_data
from ..utilities import get_httpx_client

router = APIRouter(prefix="/api/ships", tags=["resources"])

@router.get("/{ship_symbol}/resources")
async def get_ship_resources(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get resource data for a specific ship"""
    if not HAS_VALID_TOKEN:
        # Return mock resource data
        return generate_mock_resource_data(ship_symbol)
    
    try:
        # In a real implementation, this would fetch from SpaceTraders API
        # For now, return mock data since SpaceTraders doesn't have resource management
        return generate_mock_resource_data(ship_symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ship_symbol}/resources/{action}")
async def execute_resource_action(ship_symbol: str, action: str, parameters: dict = {}, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Execute a resource management action on a ship"""
    if not HAS_VALID_TOKEN:
        # Mock the resource action
        return {"status": "success", "message": f"Executed {action} on {ship_symbol}", "data": parameters}
    
    try:
        # In a real implementation, this would interact with SpaceTraders API
        # For now, simulate successful execution
        
        action_responses = {
            "optimize-fuel": {"status": "success", "message": "Fuel optimization enabled", "efficiency_increase": 5},
            "refuel": {"status": "success", "message": "Ship refueled", "fuel_added": 50},
            "balance-power": {"status": "success", "message": f"Power balanced to {parameters.get('mode', 'normal')} mode"},
            "activate-heat-sink": {"status": "success", "message": "Heat sinks activated", "temperature_reduction": 10},
            "emergency-cooling": {"status": "success", "message": "Emergency cooling engaged", "temperature_reduction": 20},
            "adjust-life-support": {"status": "success", "message": f"Life support adjusted to {parameters.get('level', 'standard')} level"},
            "start-recycling": {"status": "success", "message": "Waste recycling started", "efficiency": 75},
            "jettison-waste": {"status": "success", "message": "Waste jettisoned", "waste_removed": 10},
            "deploy-emergency": {"status": "success", "message": "Emergency protocols deployed", "supplies_used": 1},
            "resupply": {"status": "success", "message": "Resupply requested", "eta": "2 hours"}
        }
        
        return action_responses.get(action, {"status": "unknown", "message": f"Unknown action: {action}"})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ship_symbol}/resource-efficiency")
async def get_resource_efficiency(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get resource efficiency metrics for a ship"""
    try:
        import random
        return {
            "overall_efficiency": random.randint(80, 95),
            "fuel_efficiency": random.randint(85, 98),
            "power_efficiency": random.randint(75, 90),
            "thermal_efficiency": random.randint(70, 85),
            "life_support_efficiency": random.randint(85, 95),
            "waste_management_efficiency": random.randint(70, 85),
            "recommendations": [
                "Consider optimizing power distribution for better efficiency",
                "Heat levels are within optimal range",
                "Waste recycling system performing well"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ship_symbol}/emergency-protocol")
async def activate_emergency_protocol(ship_symbol: str, protocol_type: str = "standard", client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Activate emergency protocols for a ship"""
    try:
        protocols = {
            "standard": "Standard emergency protocol activated",
            "life_support": "Life support emergency protocol activated",
            "hull_breach": "Hull breach emergency protocol activated",
            "power_failure": "Power failure emergency protocol activated",
            "fire": "Fire suppression emergency protocol activated"
        }
        
        return {
            "status": "success",
            "message": protocols.get(protocol_type, "Emergency protocol activated"),
            "protocol": protocol_type,
            "emergency_supplies_used": True,
            "crew_status": "safe"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))