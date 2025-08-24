from fastapi import APIRouter, HTTPException, Depends
import httpx

from ..models import CombatActionRequest
from ..config import HAS_VALID_TOKEN
from ..mock_data import MOCK_SHIPS
from ..utilities import get_httpx_client

router = APIRouter(prefix="/api/ships", tags=["combat"])

@router.post("/{ship_symbol}/combat/weapons")
async def manage_weapons(ship_symbol: str, request: CombatActionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Arm or disarm ship weapons"""
    if not HAS_VALID_TOKEN:
        # Mock weapon management response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "ship": mock_ship,
                "action": request.action,
                "message": f"Weapons {request.action}ed successfully",
                "timestamp": "2023-11-01T00:00:00.000Z"
            }
        }
    
    # In a real implementation, this would interact with the SpaceTraders API
    return {
        "data": {
            "action": request.action,
            "message": f"Weapons {request.action}ed successfully",
            "timestamp": "2023-11-01T00:00:00.000Z"
        }
    }

@router.post("/{ship_symbol}/combat/shields")
async def manage_shields(ship_symbol: str, request: CombatActionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Activate or deactivate ship shields"""
    if not HAS_VALID_TOKEN:
        # Mock shield management response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "ship": mock_ship,
                "action": request.action,
                "message": f"Shields {request.action}d successfully",
                "timestamp": "2023-11-01T00:00:00.000Z"
            }
        }
    
    # In a real implementation, this would interact with the SpaceTraders API
    return {
        "data": {
            "action": request.action,
            "message": f"Shields {request.action}d successfully",
            "timestamp": "2023-11-01T00:00:00.000Z"
        }
    }

@router.post("/{ship_symbol}/combat/target")
async def target_acquisition(ship_symbol: str, request: CombatActionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Acquire or release target lock"""
    if not HAS_VALID_TOKEN:
        # Mock targeting response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "ship": mock_ship,
                "target": request.target,
                "locked": request.action == "acquire",
                "message": f"Target {request.action}d successfully",
                "timestamp": "2023-11-01T00:00:00.000Z"
            }
        }
    
    # In a real implementation, this would interact with the SpaceTraders API
    return {
        "data": {
            "target": request.target,
            "locked": request.action == "acquire",
            "message": f"Target {request.action}d successfully",
            "timestamp": "2023-11-01T00:00:00.000Z"
        }
    }

@router.post("/{ship_symbol}/combat/evasive")
async def evasive_maneuvers(ship_symbol: str, request: CombatActionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Engage or disengage evasive maneuvers"""
    if not HAS_VALID_TOKEN:
        # Mock evasive maneuvers response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "ship": mock_ship,
                "evasive_mode": request.action == "engage",
                "message": f"Evasive maneuvers {request.action}d successfully",
                "timestamp": "2023-11-01T00:00:00.000Z"
            }
        }
    
    # In a real implementation, this would interact with the SpaceTraders API
    return {
        "data": {
            "evasive_mode": request.action == "engage",
            "message": f"Evasive maneuvers {request.action}d successfully",
            "timestamp": "2023-11-01T00:00:00.000Z"
        }
    }

@router.post("/{ship_symbol}/combat/point-defense")
async def point_defense_system(ship_symbol: str, request: CombatActionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Activate or deactivate point defense systems"""
    if not HAS_VALID_TOKEN:
        # Mock point defense response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "ship": mock_ship,
                "point_defense_active": request.action == "activate",
                "message": f"Point defense system {request.action}d successfully",
                "timestamp": "2023-11-01T00:00:00.000Z"
            }
        }
    
    # In a real implementation, this would interact with the SpaceTraders API
    return {
        "data": {
            "point_defense_active": request.action == "activate",
            "message": f"Point defense system {request.action}d successfully",
            "timestamp": "2023-11-01T00:00:00.000Z"
        }
    }

@router.post("/{ship_symbol}/combat/missiles")
async def launch_missiles(ship_symbol: str, request: CombatActionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Launch guided missiles at target"""
    if not HAS_VALID_TOKEN:
        # Mock missile launch response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "ship": mock_ship,
                "target": request.target,
                "missiles_launched": request.params.get("count", 1) if request.params else 1,
                "message": "Missiles launched successfully",
                "timestamp": "2023-11-01T00:00:00.000Z"
            }
        }
    
    # In a real implementation, this would interact with the SpaceTraders API
    return {
        "data": {
            "target": request.target,
            "missiles_launched": request.params.get("count", 1) if request.params else 1,
            "message": "Missiles launched successfully",
            "timestamp": "2023-11-01T00:00:00.000Z"
        }
    }

@router.get("/{ship_symbol}/combat/status")
async def get_combat_status(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get current combat status of ship"""
    if not HAS_VALID_TOKEN:
        # Mock combat status response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "ship": mock_ship,
                "combat_status": {
                    "weapons_armed": False,
                    "shields_active": False,
                    "target_locked": False,
                    "evasive_mode": False,
                    "point_defense_active": False,
                    "available_weapons": len([m for m in mock_ship["mounts"] if "WEAPON" in m.get("symbol", "") or "CANNON" in m.get("symbol", "") or "LAUNCHER" in m.get("symbol", "") or "TURRET" in m.get("symbol", "")]),
                    "available_shields": len([m for m in mock_ship["modules"] if "SHIELD" in m.get("symbol", "")])
                },
                "timestamp": "2023-11-01T00:00:00.000Z"
            }
        }
    
    # In a real implementation, this would interact with the SpaceTraders API
    return {
        "data": {
            "combat_status": {
                "weapons_armed": False,
                "shields_active": False,
                "target_locked": False,
                "evasive_mode": False,
                "point_defense_active": False
            },
            "timestamp": "2023-11-01T00:00:00.000Z"
        }
    }