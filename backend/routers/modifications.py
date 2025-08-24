from fastapi import APIRouter, HTTPException
from ..models import ModificationRequest, CustomizationRequest
from ..config import SHIP_COLORS, SHIP_DECALS
from ..mock_data import MOCK_SHIPS, MOCK_AGENT, MOCK_EQUIPMENT

router = APIRouter(prefix="/api", tags=["modifications"])

@router.get("/equipment")
async def get_equipment():
    """Get available equipment for ship modifications"""
    return {"data": MOCK_EQUIPMENT}

@router.get("/equipment/{component_type}")
async def get_equipment_by_type(component_type: str):
    """Get equipment by type (modules, mounts, reactors, engines)"""
    if component_type not in MOCK_EQUIPMENT:
        raise HTTPException(status_code=404, detail="Component type not found")
    return {"data": MOCK_EQUIPMENT[component_type]}

@router.post("/ships/{ship_symbol}/install")
async def install_component(ship_symbol: str, request: ModificationRequest):
    """Install a module or mount on a ship"""
    # Find the ship
    ship = next((s for s in MOCK_SHIPS if s["symbol"] == ship_symbol), None)
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    # Find the component in equipment
    component_data = None
    if request.componentType in MOCK_EQUIPMENT:
        component_data = next((c for c in MOCK_EQUIPMENT[request.componentType] if c["symbol"] == request.componentSymbol), None)
    
    if not component_data:
        raise HTTPException(status_code=404, detail="Component not found")
    
    # Check if agent has enough credits
    if MOCK_AGENT["credits"] < component_data["price"]:
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    # Install the component
    if request.componentType == "modules":
        ship["modules"].append({
            "symbol": component_data["symbol"],
            "name": component_data["name"],
            "description": component_data["description"],
            "capacity": component_data.get("capacity"),
            "range": component_data.get("range"),
            "requirements": component_data["requirements"]
        })
    elif request.componentType == "mounts":
        ship["mounts"].append({
            "symbol": component_data["symbol"],
            "name": component_data["name"],
            "description": component_data["description"],
            "strength": component_data.get("strength"),
            "deposits": component_data.get("deposits"),
            "requirements": component_data["requirements"]
        })
    elif request.componentType == "reactors":
        ship["reactor"] = {
            "symbol": component_data["symbol"],
            "name": component_data["name"],
            "description": component_data["description"],
            "powerOutput": component_data["powerOutput"],
            "requirements": component_data["requirements"]
        }
    elif request.componentType == "engines":
        ship["engine"] = {
            "symbol": component_data["symbol"],
            "name": component_data["name"],
            "description": component_data["description"],
            "speed": component_data["speed"],
            "requirements": component_data["requirements"]
        }
    
    # Deduct credits
    MOCK_AGENT["credits"] -= component_data["price"]
    
    return {
        "data": {
            "ship": ship,
            "transaction": {
                "component": component_data,
                "price": component_data["price"],
                "creditsRemaining": MOCK_AGENT["credits"]
            }
        }
    }

@router.post("/ships/{ship_symbol}/remove")
async def remove_component(ship_symbol: str, request: ModificationRequest):
    """Remove a module or mount from a ship"""
    ship = next((s for s in MOCK_SHIPS if s["symbol"] == ship_symbol), None)
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    removed_component = None
    refund_amount = 0
    
    if request.componentType == "modules":
        for i, module in enumerate(ship["modules"]):
            if module.get("symbol") == request.componentSymbol:
                removed_component = ship["modules"].pop(i)
                break
    elif request.componentType == "mounts":
        for i, mount in enumerate(ship["mounts"]):
            if mount.get("symbol") == request.componentSymbol:
                removed_component = ship["mounts"].pop(i)
                break
    
    if not removed_component:
        raise HTTPException(status_code=404, detail="Component not found on ship")
    
    # Calculate refund (50% of original price)
    component_data = None
    if request.componentType in MOCK_EQUIPMENT:
        component_data = next((c for c in MOCK_EQUIPMENT[request.componentType] if c["symbol"] == request.componentSymbol), None)
    
    if component_data:
        refund_amount = component_data["price"] // 2
        MOCK_AGENT["credits"] += refund_amount
    
    return {
        "data": {
            "ship": ship,
            "transaction": {
                "removedComponent": removed_component,
                "refund": refund_amount,
                "creditsRemaining": MOCK_AGENT["credits"]
            }
        }
    }

@router.post("/ships/{ship_symbol}/customize")
async def customize_ship(ship_symbol: str, request: CustomizationRequest):
    """Customize ship appearance (name, color, decals)"""
    ship = next((s for s in MOCK_SHIPS if s["symbol"] == ship_symbol), None)
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    customization_cost = 1000  # Base cost for customization
    total_cost = 0
    
    if request.name:
        ship["registration"]["name"] = request.name
        total_cost += customization_cost
    
    if request.color:
        if request.color not in SHIP_COLORS:
            raise HTTPException(status_code=400, detail="Invalid color")
        if "customization" not in ship:
            ship["customization"] = {}
        ship["customization"]["color"] = request.color
        total_cost += customization_cost
    
    if request.decal:
        if request.decal not in SHIP_DECALS:
            raise HTTPException(status_code=400, detail="Invalid decal")
        if "customization" not in ship:
            ship["customization"] = {}
        ship["customization"]["decal"] = request.decal
        total_cost += customization_cost
    
    if MOCK_AGENT["credits"] < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient credits for customization")
    
    MOCK_AGENT["credits"] -= total_cost
    
    return {
        "data": {
            "ship": ship,
            "transaction": {
                "customizationCost": total_cost,
                "creditsRemaining": MOCK_AGENT["credits"]
            }
        }
    }

@router.get("/ships/{ship_symbol}/modification-info")
async def get_ship_modification_info(ship_symbol: str):
    """Get ship modification capabilities and current status"""
    ship = next((s for s in MOCK_SHIPS if s["symbol"] == ship_symbol), None)
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    # Calculate current power usage
    current_power_usage = 0
    for module in ship.get("modules", []):
        if "requirements" in module:
            current_power_usage += module["requirements"].get("power", 0)
    for mount in ship.get("mounts", []):
        if "requirements" in mount:
            current_power_usage += mount["requirements"].get("power", 0)
    
    reactor_power = ship.get("reactor", {}).get("powerOutput", 10)  # Default power
    
    # Mock frame data
    frame_data = {
        "moduleSlots": 8,
        "mountingPoints": 4,
        "usedModuleSlots": len(ship.get("modules", [])),
        "usedMountingPoints": len(ship.get("mounts", []))
    }
    
    return {
        "data": {
            "ship": ship,
            "powerInfo": {
                "reactorPower": reactor_power,
                "currentUsage": current_power_usage,
                "availablePower": reactor_power - current_power_usage
            },
            "slotInfo": frame_data,
            "availableColors": SHIP_COLORS,
            "availableDecals": SHIP_DECALS
        }
    }