from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Union
import httpx
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="SpaceTraders GUI Backend", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SPACETRADERS_TOKEN = os.getenv("SPACETRADERS_TOKEN")
SPACETRADERS_CALLSIGN = os.getenv("SPACETRADERS_CALLSIGN")
SPACETRADERS_API_URL = os.getenv("SPACETRADERS_API_URL", "https://api.spacetraders.io/v2")

# Check if we have a valid token
HAS_VALID_TOKEN = SPACETRADERS_TOKEN and SPACETRADERS_TOKEN != "demo_token_for_testing"

# HTTP client for SpaceTraders API
async def get_httpx_client():
    async with httpx.AsyncClient() as client:
        yield client

# Pydantic models
class Agent(BaseModel):
    symbol: str
    headquarters: str
    credits: int
    startingFaction: str

class ShipRequirements(BaseModel):
    power: int
    crew: int
    slots: int

class ShipComponent(BaseModel):
    symbol: str
    name: str
    description: str
    condition: float = 1.0
    integrity: float = 1.0
    requirements: ShipRequirements
    quality: int = 1

class ShipFrame(ShipComponent):
    moduleSlots: int
    mountingPoints: int
    fuelCapacity: int

class ShipReactor(ShipComponent):
    powerOutput: int

class ShipEngine(ShipComponent):
    speed: int

class ShipModule(BaseModel):
    symbol: str
    name: str
    description: str
    capacity: Optional[int] = None
    range: Optional[int] = None
    requirements: ShipRequirements

class ShipMount(BaseModel):
    symbol: str
    name: str
    description: str
    strength: Optional[int] = None
    deposits: Optional[List[str]] = None
    requirements: ShipRequirements

class Ship(BaseModel):
    symbol: str
    registration: dict
    nav: dict
    crew: dict
    frame: dict
    reactor: dict
    engine: dict
    modules: List[dict]
    mounts: List[dict]
    cargo: dict

class EquipmentItem(BaseModel):
    component: Union[ShipModule, ShipMount, ShipReactor, ShipEngine, ShipFrame]
    price: int
    available: bool = True

class ModificationRequest(BaseModel):
    shipSymbol: str
    componentType: str  # "module", "mount", "reactor", "engine", "frame"
    componentSymbol: str
    action: str  # "install", "remove", "upgrade"

class CustomizationRequest(BaseModel):
    shipSymbol: str
    name: Optional[str] = None
    color: Optional[str] = None
    decal: Optional[str] = None

class System(BaseModel):
    symbol: str
    sectorSymbol: str
    type: str
    x: int
    y: int
    waypoints: List[dict]
    factions: List[dict]

class Waypoint(BaseModel):
    symbol: str
    type: str
    systemSymbol: str
    x: int
    y: int
    orbitals: List[dict] = []
    traits: List[dict] = []
    chart: Optional[dict] = None
    faction: Optional[dict] = None

class NavigateRequest(BaseModel):
    waypointSymbol: str

# Mock data for testing
MOCK_AGENT = {
    "symbol": "DEMO_AGENT",
    "headquarters": "X1-DF55-20250X",
    "credits": 1000000,
    "startingFaction": "COSMIC"
}

MOCK_SHIPS = [
    {
        "symbol": "DEMO_SHIP_1",
        "registration": {"name": "Explorer One", "role": "EXPLORER"},
        "nav": {
            "status": "IN_ORBIT", 
            "waypointSymbol": "X1-DF55-20250X",
            "systemSymbol": "X1-DF55",
            "route": {
                "destination": {
                    "symbol": "X1-DF55-20250X",
                    "type": "PLANET",
                    "systemSymbol": "X1-DF55",
                    "x": -42,
                    "y": -26
                },
                "origin": {
                    "symbol": "X1-DF55-20250X",
                    "type": "PLANET",
                    "systemSymbol": "X1-DF55",
                    "x": -42,
                    "y": -26
                },
                "departureTime": "2023-11-01T00:00:00.000Z",
                "arrival": "2023-11-01T00:00:00.000Z"
            }
        },
        "crew": {"current": 2, "capacity": 4},
        "frame": {"name": "Explorer Frame", "symbol": "FRAME_EXPLORER"},
        "reactor": {"name": "Basic Reactor", "symbol": "REACTOR_SOLAR_I", "powerOutput": 10},
        "engine": {"name": "Basic Engine", "symbol": "ENGINE_IMPULSE_DRIVE_I", "speed": 20},
        "modules": [{"name": "Basic Module", "symbol": "MODULE_CARGO_HOLD_I", "description": "Basic cargo storage"}],
        "mounts": [{"name": "Basic Mount", "symbol": "MOUNT_SENSOR_ARRAY_I", "description": "Basic sensor array"}],
        "cargo": {"units": 50, "capacity": 100, "inventory": [{"symbol": "FUEL", "units": 50}]}
    }
]

MOCK_SYSTEMS = [
    {
        "symbol": "X1-DF55",
        "sectorSymbol": "X1",
        "type": "NEUTRON_STAR",
        "x": 0,
        "y": 0,
        "waypoints": [
            {"symbol": "X1-DF55-20250X", "type": "PLANET", "x": -42, "y": -26},
            {"symbol": "X1-DF55-20250Y", "type": "ASTEROID_FIELD", "x": 18, "y": -175},
            {"symbol": "X1-DF55-20250Z", "type": "JUMP_GATE", "x": 48, "y": 12},
            {"symbol": "X1-DF55-20250A", "type": "GAS_GIANT", "x": -85, "y": 92},
            {"symbol": "X1-DF55-20250B", "type": "MOON", "x": -38, "y": -15}
        ],
        "factions": [{"symbol": "COSMIC"}]
    }
]

MOCK_WAYPOINTS = [
    {
        "symbol": "X1-DF55-20250X",
        "type": "PLANET",
        "systemSymbol": "X1-DF55",
        "x": -42,
        "y": -26,
        "orbitals": [{"symbol": "X1-DF55-20250B"}],
        "traits": [
            {"symbol": "MARKETPLACE", "name": "Marketplace", "description": "A thriving marketplace where goods and services are traded."},
            {"symbol": "SHIPYARD", "name": "Shipyard", "description": "A facility where ships are constructed, repaired, and outfitted."}
        ],
        "faction": {"symbol": "COSMIC"}
    },
    {
        "symbol": "X1-DF55-20250Y",
        "type": "ASTEROID_FIELD",
        "systemSymbol": "X1-DF55",
        "x": 18,
        "y": -175,
        "orbitals": [],
        "traits": [
            {"symbol": "COMMON_METAL_DEPOSITS", "name": "Common Metal Deposits", "description": "Large deposits of common metals."},
            {"symbol": "RARE_METAL_DEPOSITS", "name": "Rare Metal Deposits", "description": "Rare metal deposits."}
        ]
    },
    {
        "symbol": "X1-DF55-20250Z",
        "type": "JUMP_GATE",
        "systemSymbol": "X1-DF55",
        "x": 48,
        "y": 12,
        "orbitals": [],
        "traits": [
            {"symbol": "UNCHARTED", "name": "Uncharted", "description": "An uncharted waypoint."}
        ]
    },
    {
        "symbol": "X1-DF55-20250A",
        "type": "GAS_GIANT",
        "systemSymbol": "X1-DF55",
        "x": -85,
        "y": 92,
        "orbitals": [],
        "traits": [
            {"symbol": "FROZEN", "name": "Frozen", "description": "A cold, frozen world."}
        ]
    },
    {
        "symbol": "X1-DF55-20250B",
        "type": "MOON",
        "systemSymbol": "X1-DF55",
        "x": -38,
        "y": -15,
        "orbitals": [],
        "traits": [
            {"symbol": "MINERAL_DEPOSITS", "name": "Mineral Deposits", "description": "Natural mineral deposits."}
        ]
    }
]

MOCK_FACTIONS = [
    {
        "symbol": "COSMIC",
        "name": "Cosmic Coalition",
        "description": "A powerful coalition of space-faring civilizations",
        "headquarters": "X1-DF55-20250X",
        "isRecruiting": True,
        "traits": [
            {"name": "Bureaucratic", "description": "Highly organized and bureaucratic"},
            {"name": "Secretive", "description": "Keeps information close to the chest"}
        ]
    }
]

# Mock equipment data for ship modifications
MOCK_EQUIPMENT = {
    "modules": [
        {
            "symbol": "MODULE_CARGO_HOLD_I",
            "name": "Cargo Hold I",
            "description": "Expand your ship's cargo capacity",
            "capacity": 30,
            "requirements": {"power": 1, "crew": 0, "slots": 1},
            "price": 5000
        },
        {
            "symbol": "MODULE_CARGO_HOLD_II", 
            "name": "Cargo Hold II",
            "description": "Advanced cargo storage system",
            "capacity": 50,
            "requirements": {"power": 2, "crew": 0, "slots": 2},
            "price": 12000
        },
        {
            "symbol": "MODULE_MINERAL_PROCESSOR_I",
            "name": "Mineral Processor I",
            "description": "Process raw minerals into refined goods",
            "requirements": {"power": 3, "crew": 1, "slots": 2},
            "price": 15000
        },
        {
            "symbol": "MODULE_FUEL_REFINERY_I",
            "name": "Fuel Refinery I", 
            "description": "Refine fuel from raw materials",
            "requirements": {"power": 4, "crew": 2, "slots": 3},
            "price": 25000
        },
        {
            "symbol": "MODULE_JUMP_DRIVE_I",
            "name": "Jump Drive I",
            "description": "Enable instant travel between systems",
            "range": 2000,
            "requirements": {"power": 8, "crew": 1, "slots": 4},
            "price": 50000
        },
        {
            "symbol": "MODULE_SHIELD_GENERATOR_I",
            "name": "Shield Generator I",
            "description": "Basic shield protection",
            "requirements": {"power": 5, "crew": 0, "slots": 2},
            "price": 18000
        }
    ],
    "mounts": [
        {
            "symbol": "MOUNT_MINING_LASER_I",
            "name": "Mining Laser I",
            "description": "Basic mining laser for extracting resources",
            "strength": 10,
            "deposits": ["IRON", "COPPER", "ALUMINUM"],
            "requirements": {"power": 2, "crew": 0, "slots": 1},
            "price": 8000
        },
        {
            "symbol": "MOUNT_MINING_LASER_II", 
            "name": "Mining Laser II",
            "description": "Advanced mining laser with higher yield",
            "strength": 25,
            "deposits": ["IRON", "COPPER", "ALUMINUM", "GOLD", "PLATINUM"],
            "requirements": {"power": 4, "crew": 0, "slots": 2},
            "price": 20000
        },
        {
            "symbol": "MOUNT_SURVEYOR_I",
            "name": "Surveyor I",
            "description": "Survey waypoints for valuable resources",
            "strength": 5,
            "requirements": {"power": 2, "crew": 1, "slots": 1},
            "price": 10000
        },
        {
            "symbol": "MOUNT_SENSOR_ARRAY_I",
            "name": "Sensor Array I", 
            "description": "Advanced sensors for detecting ships and hazards",
            "requirements": {"power": 3, "crew": 0, "slots": 1},
            "price": 12000
        },
        {
            "symbol": "MOUNT_GAS_SIPHON_I",
            "name": "Gas Siphon I",
            "description": "Extract gases from gas giants",
            "strength": 8,
            "deposits": ["HYDROCARBON"],
            "requirements": {"power": 3, "crew": 1, "slots": 2},
            "price": 15000
        },
        {
            "symbol": "MOUNT_LASER_CANNON_I",
            "name": "Laser Cannon I",
            "description": "Basic weapon system for ship defense",
            "strength": 15,
            "requirements": {"power": 5, "crew": 0, "slots": 1},
            "price": 22000
        }
    ],
    "reactors": [
        {
            "symbol": "REACTOR_FUSION_I",
            "name": "Fusion Reactor I",
            "description": "Advanced fusion reactor with higher power output",
            "powerOutput": 15,
            "requirements": {"power": 0, "crew": 2, "slots": 0},
            "price": 35000
        },
        {
            "symbol": "REACTOR_ANTIMATTER_I",
            "name": "Antimatter Reactor I", 
            "description": "Cutting-edge antimatter reactor",
            "powerOutput": 25,
            "requirements": {"power": 0, "crew": 3, "slots": 0},
            "price": 75000
        }
    ],
    "engines": [
        {
            "symbol": "ENGINE_ION_DRIVE_I",
            "name": "Ion Drive I",
            "description": "Efficient ion propulsion system",
            "speed": 25,
            "requirements": {"power": 4, "crew": 0, "slots": 0},
            "price": 28000
        },
        {
            "symbol": "ENGINE_HYPER_DRIVE_I", 
            "name": "Hyper Drive I",
            "description": "Ultra-fast hyperdrive engine",
            "speed": 40,
            "requirements": {"power": 8, "crew": 1, "slots": 0},
            "price": 60000
        }
    ]
}

# Available ship customizations
SHIP_COLORS = ["red", "blue", "green", "gold", "silver", "black", "white", "purple"]
SHIP_DECALS = ["flames", "stars", "stripes", "dragon", "eagle", "skull", "lightning", "geometric"]

# API endpoints
@app.get("/")
async def root():
    return {"message": "SpaceTraders GUI Backend API"}

@app.get("/api/status")
async def get_status():
    """Get SpaceTraders API status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SPACETRADERS_API_URL}")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent", response_model=Agent)
async def get_agent(client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get current agent information"""
    if not HAS_VALID_TOKEN:
        return MOCK_AGENT
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/agent", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ships", response_model=List[Ship])
async def get_ships(client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get all ships for the current agent"""
    if not HAS_VALID_TOKEN:
        return MOCK_SHIPS
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/ships", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/systems", response_model=List[System])
async def get_systems(client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get all systems"""
    if not HAS_VALID_TOKEN:
        return MOCK_SYSTEMS
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/systems", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/factions")
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

@app.get("/api/info")
async def get_info():
    """Get application info and token status"""
    return {
        "has_valid_token": HAS_VALID_TOKEN,
        "token_configured": bool(SPACETRADERS_TOKEN),
        "callsign_configured": bool(SPACETRADERS_CALLSIGN),
        "api_url": SPACETRADERS_API_URL,
        "message": "Use demo data" if not HAS_VALID_TOKEN else "Using real SpaceTraders API"
    }

@app.get("/api/systems/{system_symbol}/waypoints", response_model=List[Waypoint])
async def get_system_waypoints(system_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get all waypoints in a system"""
    if not HAS_VALID_TOKEN:
        # Return mock waypoints for the demo system
        if system_symbol == "X1-DF55":
            return MOCK_WAYPOINTS
        else:
            return []
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/systems/{system_symbol}/waypoints", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/systems/{system_symbol}", response_model=System)
async def get_system(system_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get system details"""
    if not HAS_VALID_TOKEN:
        # Return mock system for demo
        if system_symbol == "X1-DF55":
            return MOCK_SYSTEMS[0]
        else:
            raise HTTPException(status_code=404, detail="System not found")
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/systems/{system_symbol}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data["data"]
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/navigate")
async def navigate_ship(ship_symbol: str, request: NavigateRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Navigate ship to a waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock navigation response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        target_waypoint = next((wp for wp in MOCK_WAYPOINTS if wp["symbol"] == request.waypointSymbol), None)
        if not target_waypoint:
            raise HTTPException(status_code=404, detail="Waypoint not found")
        
        # Update mock ship navigation
        mock_ship["nav"]["waypointSymbol"] = request.waypointSymbol
        mock_ship["nav"]["status"] = "IN_TRANSIT"
        mock_ship["nav"]["route"]["destination"] = {
            "symbol": target_waypoint["symbol"],
            "type": target_waypoint["type"],
            "systemSymbol": target_waypoint["systemSymbol"],
            "x": target_waypoint["x"],
            "y": target_waypoint["y"]
        }
        
        return {
            "data": {
                "fuel": {"current": 48, "capacity": 100, "consumed": {"amount": 2, "timestamp": "2023-11-01T00:00:00.000Z"}},
                "nav": mock_ship["nav"]
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {"waypointSymbol": request.waypointSymbol}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/navigate", 
                                   json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/dock")
async def dock_ship(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Dock ship at current waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock dock response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        mock_ship["nav"]["status"] = "DOCKED"
        return {"data": {"nav": mock_ship["nav"]}}
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/dock", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/orbit")
async def orbit_ship(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Put ship in orbit around current waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock orbit response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        mock_ship["nav"]["status"] = "IN_ORBIT"
        return {"data": {"nav": mock_ship["nav"]}}
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/orbit", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ship modification endpoints
@app.get("/api/equipment")
async def get_equipment():
    """Get available equipment for ship modifications"""
    return {"data": MOCK_EQUIPMENT}

@app.get("/api/equipment/{component_type}")
async def get_equipment_by_type(component_type: str):
    """Get equipment by type (modules, mounts, reactors, engines)"""
    if component_type not in MOCK_EQUIPMENT:
        raise HTTPException(status_code=404, detail="Component type not found")
    return {"data": MOCK_EQUIPMENT[component_type]}

@app.post("/api/ships/{ship_symbol}/install")
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

@app.post("/api/ships/{ship_symbol}/remove")
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

@app.post("/api/ships/{ship_symbol}/customize")
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

@app.get("/api/ships/{ship_symbol}/modification-info")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
