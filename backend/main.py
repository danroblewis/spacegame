from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
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

# Fleet Management Models
class FleetFormation(BaseModel):
    name: str
    type: str  # "line", "wedge", "box", "circle", "custom"
    leader_ship: str
    member_ships: List[str]
    positions: dict  # ship_symbol -> {x_offset, y_offset}
    active: bool = True

class FleetGroup(BaseModel):
    name: str
    ships: List[str]
    role: Optional[str] = None  # "combat", "mining", "transport", "exploration"
    formation: Optional[str] = None
    active: bool = True

class FleetCommand(BaseModel):
    command_type: str  # "navigate", "dock", "orbit", "mine", "attack", "formation"
    target_ships: List[str]  # ship symbols or group names
    parameters: dict
    priority: int = 1

class ResourceTransferRequest(BaseModel):
    from_ship: str
    to_ship: str
    resource_symbol: str
    quantity: int

class SupplyRoute(BaseModel):
    name: str
    source_waypoint: str
    destination_waypoint: str
    resource_types: List[str]
    assigned_ships: List[str]
    active: bool = True
    schedule: Optional[dict] = None  # for automated runs

class FleetOperation(BaseModel):
    operation_id: str
    operation_type: str  # "mining", "trading", "exploration", "combat"
    assigned_ships: List[str]
    target_location: str
    status: str  # "pending", "active", "completed", "cancelled"
    progress: dict
    estimated_completion: Optional[str] = None

class CombatTarget(BaseModel):
    target_type: str  # "ship", "station", "pirate"
    target_id: str
    location: str
    threat_level: int  # 1-10
    estimated_health: int

class CombatFormation(BaseModel):
    formation_id: str
    name: str
    ships: List[str]
    roles: dict  # ship_symbol -> role (tank, dps, support)
    target: str
    tactics: str  # "alpha_strike", "surround", "hit_and_run"
    status: str  # "forming", "engaging", "completed"

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
        "frame": {"name": "Explorer Frame"},
        "reactor": {"name": "Basic Reactor"},
        "engine": {"name": "Basic Engine"},
        "modules": [{"name": "Basic Module"}],
        "mounts": [{"name": "Basic Mount"}],
        "cargo": {"units": 50, "capacity": 100, "inventory": [{"symbol": "FUEL", "units": 50}]}
    },
    {
        "symbol": "DEMO_SHIP_2",
        "registration": {"name": "Cargo Hauler", "role": "HAULER"},
        "nav": {
            "status": "DOCKED", 
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
        "crew": {"current": 3, "capacity": 6},
        "frame": {"name": "Hauler Frame"},
        "reactor": {"name": "Basic Reactor"},
        "engine": {"name": "Fast Engine"},
        "modules": [{"name": "Cargo Module"}],
        "mounts": [{"name": "Basic Mount"}],
        "cargo": {"units": 80, "capacity": 200, "inventory": [{"symbol": "FUEL", "units": 30}, {"symbol": "IRON_ORE", "units": 50}]}
    },
    {
        "symbol": "DEMO_SHIP_3",
        "registration": {"name": "Mining Vessel", "role": "EXCAVATOR"},
        "nav": {
            "status": "IN_ORBIT", 
            "waypointSymbol": "X1-DF55-20250Y",
            "systemSymbol": "X1-DF55",
            "route": {
                "destination": {
                    "symbol": "X1-DF55-20250Y",
                    "type": "ASTEROID_FIELD",
                    "systemSymbol": "X1-DF55",
                    "x": 18,
                    "y": -175
                },
                "origin": {
                    "symbol": "X1-DF55-20250Y",
                    "type": "ASTEROID_FIELD",
                    "systemSymbol": "X1-DF55",
                    "x": 18,
                    "y": -175
                },
                "departureTime": "2023-11-01T00:00:00.000Z",
                "arrival": "2023-11-01T00:00:00.000Z"
            }
        },
        "crew": {"current": 4, "capacity": 8},
        "frame": {"name": "Mining Frame"},
        "reactor": {"name": "High Power Reactor"},
        "engine": {"name": "Basic Engine"},
        "modules": [{"name": "Mining Module"}],
        "mounts": [{"name": "Mining Laser"}],
        "cargo": {"units": 75, "capacity": 150, "inventory": [{"symbol": "FUEL", "units": 25}, {"symbol": "COPPER_ORE", "units": 50}]}
    }
]

# Fleet Management Mock Data
MOCK_FLEET_GROUPS = [
    {
        "name": "Mining Fleet",
        "ships": ["DEMO_SHIP_3"],
        "role": "mining",
        "formation": None,
        "active": True
    },
    {
        "name": "Transport Fleet", 
        "ships": ["DEMO_SHIP_2"],
        "role": "transport",
        "formation": None,
        "active": True
    },
    {
        "name": "Exploration Fleet",
        "ships": ["DEMO_SHIP_1"],
        "role": "exploration", 
        "formation": None,
        "active": True
    }
]

MOCK_FORMATIONS = [
    {
        "name": "Line Formation",
        "type": "line",
        "leader_ship": "DEMO_SHIP_1",
        "member_ships": ["DEMO_SHIP_2", "DEMO_SHIP_3"],
        "positions": {
            "DEMO_SHIP_1": {"x_offset": 0, "y_offset": 0},
            "DEMO_SHIP_2": {"x_offset": -5, "y_offset": 0},
            "DEMO_SHIP_3": {"x_offset": 5, "y_offset": 0}
        },
        "active": False
    },
    {
        "name": "Mining Formation",
        "type": "circle",
        "leader_ship": "DEMO_SHIP_2",
        "member_ships": ["DEMO_SHIP_3"],
        "positions": {
            "DEMO_SHIP_2": {"x_offset": 0, "y_offset": 0},
            "DEMO_SHIP_3": {"x_offset": 10, "y_offset": 0}
        },
        "active": False
    }
]

MOCK_SUPPLY_ROUTES = [
    {
        "name": "Ore Transport Route",
        "source_waypoint": "X1-DF55-20250Y",
        "destination_waypoint": "X1-DF55-20250X",
        "resource_types": ["IRON_ORE", "COPPER_ORE"],
        "assigned_ships": ["DEMO_SHIP_2"],
        "active": True,
        "schedule": {"frequency": "daily", "auto_start": True}
    }
]

MOCK_FLEET_OPERATIONS = [
    {
        "operation_id": "OP_001",
        "operation_type": "mining",
        "assigned_ships": ["DEMO_SHIP_3"],
        "target_location": "X1-DF55-20250Y",
        "status": "active",
        "progress": {"extracted": 50, "target": 100},
        "estimated_completion": "2023-11-01T02:00:00.000Z"
    }
]

# Combat Mock Data
MOCK_COMBAT_TARGETS = [
    {
        "target_type": "pirate",
        "target_id": "PIRATE_RAIDER_1",
        "location": "X1-DF55-20250Z",
        "threat_level": 6,
        "estimated_health": 100
    },
    {
        "target_type": "station",
        "target_id": "HOSTILE_OUTPOST_1",
        "location": "X1-DF55-20250A",
        "threat_level": 8,
        "estimated_health": 500
    }
]

MOCK_COMBAT_FORMATIONS = [
    {
        "formation_id": "CF_001",
        "name": "Alpha Strike Formation",
        "ships": ["DEMO_SHIP_1", "DEMO_SHIP_2"],
        "roles": {
            "DEMO_SHIP_1": "scout",
            "DEMO_SHIP_2": "support"
        },
        "target": "PIRATE_RAIDER_1",
        "tactics": "alpha_strike",
        "status": "forming"
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

# Fleet Management API Endpoints

@app.get("/api/fleet/groups", response_model=List[FleetGroup])
async def get_fleet_groups():
    """Get all fleet groups"""
    return MOCK_FLEET_GROUPS

@app.post("/api/fleet/groups")
async def create_fleet_group(group: FleetGroup):
    """Create a new fleet group"""
    MOCK_FLEET_GROUPS.append(group.dict())
    return {"message": "Fleet group created successfully", "group": group}

@app.put("/api/fleet/groups/{group_name}")
async def update_fleet_group(group_name: str, group: FleetGroup):
    """Update an existing fleet group"""
    for i, existing_group in enumerate(MOCK_FLEET_GROUPS):
        if existing_group["name"] == group_name:
            MOCK_FLEET_GROUPS[i] = group.dict()
            return {"message": "Fleet group updated successfully", "group": group}
    raise HTTPException(status_code=404, detail="Fleet group not found")

@app.delete("/api/fleet/groups/{group_name}")
async def delete_fleet_group(group_name: str):
    """Delete a fleet group"""
    for i, group in enumerate(MOCK_FLEET_GROUPS):
        if group["name"] == group_name:
            del MOCK_FLEET_GROUPS[i]
            return {"message": "Fleet group deleted successfully"}
    raise HTTPException(status_code=404, detail="Fleet group not found")

@app.get("/api/fleet/formations", response_model=List[FleetFormation])
async def get_formations():
    """Get all fleet formations"""
    return MOCK_FORMATIONS

@app.post("/api/fleet/formations")
async def create_formation(formation: FleetFormation):
    """Create a new fleet formation"""
    MOCK_FORMATIONS.append(formation.dict())
    return {"message": "Formation created successfully", "formation": formation}

@app.post("/api/fleet/formations/{formation_name}/activate")
async def activate_formation(formation_name: str):
    """Activate a fleet formation"""
    for formation in MOCK_FORMATIONS:
        if formation["name"] == formation_name:
            formation["active"] = True
            # Move ships to formation positions
            for ship_symbol, position in formation["positions"].items():
                for ship in MOCK_SHIPS:
                    if ship["symbol"] == ship_symbol:
                        # Update ship position (in real implementation, this would send navigate commands)
                        ship["nav"]["status"] = "IN_FORMATION"
                        break
            return {"message": f"Formation {formation_name} activated"}
    raise HTTPException(status_code=404, detail="Formation not found")

@app.post("/api/fleet/formations/{formation_name}/deactivate")
async def deactivate_formation(formation_name: str):
    """Deactivate a fleet formation"""
    for formation in MOCK_FORMATIONS:
        if formation["name"] == formation_name:
            formation["active"] = False
            # Reset ship statuses
            for ship_symbol in formation["member_ships"] + [formation["leader_ship"]]:
                for ship in MOCK_SHIPS:
                    if ship["symbol"] == ship_symbol:
                        if ship["nav"]["status"] == "IN_FORMATION":
                            ship["nav"]["status"] = "IN_ORBIT"
                        break
            return {"message": f"Formation {formation_name} deactivated"}
    raise HTTPException(status_code=404, detail="Formation not found")

@app.post("/api/fleet/commands")
async def execute_fleet_command(command: FleetCommand):
    """Execute a fleet command"""
    results = []
    
    for target in command.target_ships:
        # Check if target is a ship symbol or group name
        if any(ship["symbol"] == target for ship in MOCK_SHIPS):
            # Single ship command
            ship = next(ship for ship in MOCK_SHIPS if ship["symbol"] == target)
            result = await execute_ship_command(ship, command.command_type, command.parameters)
            results.append({"ship": target, "result": result})
        else:
            # Group command
            group = next((g for g in MOCK_FLEET_GROUPS if g["name"] == target), None)
            if group:
                for ship_symbol in group["ships"]:
                    ship = next(ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol)
                    result = await execute_ship_command(ship, command.command_type, command.parameters)
                    results.append({"ship": ship_symbol, "result": result})
    
    return {"message": "Fleet command executed", "results": results}

async def execute_ship_command(ship: dict, command_type: str, parameters: dict):
    """Execute a command on a single ship"""
    if command_type == "navigate":
        ship["nav"]["waypointSymbol"] = parameters["waypointSymbol"]
        ship["nav"]["status"] = "IN_TRANSIT"
        return "Navigating to " + parameters["waypointSymbol"]
    elif command_type == "dock":
        ship["nav"]["status"] = "DOCKED"
        return "Docked"
    elif command_type == "orbit":
        ship["nav"]["status"] = "IN_ORBIT"
        return "In orbit"
    elif command_type == "mine":
        if ship["registration"]["role"] in ["EXCAVATOR", "SURVEYOR"]:
            return "Mining started"
        else:
            return "Ship cannot mine"
    return "Command executed"

@app.post("/api/fleet/transfer")
async def transfer_resources(transfer: ResourceTransferRequest):
    """Transfer resources between ships"""
    from_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == transfer.from_ship), None)
    to_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == transfer.to_ship), None)
    
    if not from_ship or not to_ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    
    # Check if ships are at the same location
    if from_ship["nav"]["waypointSymbol"] != to_ship["nav"]["waypointSymbol"]:
        raise HTTPException(status_code=400, detail="Ships must be at the same location")
    
    # Find resource in from_ship
    from_inventory = from_ship["cargo"]["inventory"]
    resource_item = next((item for item in from_inventory if item["symbol"] == transfer.resource_symbol), None)
    
    if not resource_item or resource_item["units"] < transfer.quantity:
        raise HTTPException(status_code=400, detail="Insufficient resources")
    
    # Check cargo space in to_ship
    to_cargo = to_ship["cargo"]
    if to_cargo["units"] + transfer.quantity > to_cargo["capacity"]:
        raise HTTPException(status_code=400, detail="Insufficient cargo space")
    
    # Perform transfer
    resource_item["units"] -= transfer.quantity
    if resource_item["units"] == 0:
        from_inventory.remove(resource_item)
    
    from_ship["cargo"]["units"] -= transfer.quantity
    
    # Add to destination ship
    to_inventory = to_ship["cargo"]["inventory"]
    existing_item = next((item for item in to_inventory if item["symbol"] == transfer.resource_symbol), None)
    
    if existing_item:
        existing_item["units"] += transfer.quantity
    else:
        to_inventory.append({"symbol": transfer.resource_symbol, "units": transfer.quantity})
    
    to_ship["cargo"]["units"] += transfer.quantity
    
    return {
        "message": f"Transferred {transfer.quantity} {transfer.resource_symbol} from {transfer.from_ship} to {transfer.to_ship}",
        "from_ship": from_ship,
        "to_ship": to_ship
    }

@app.get("/api/fleet/supply-routes", response_model=List[SupplyRoute])
async def get_supply_routes():
    """Get all supply routes"""
    return MOCK_SUPPLY_ROUTES

@app.post("/api/fleet/supply-routes")
async def create_supply_route(route: SupplyRoute):
    """Create a new supply route"""
    MOCK_SUPPLY_ROUTES.append(route.dict())
    return {"message": "Supply route created successfully", "route": route}

@app.post("/api/fleet/supply-routes/{route_name}/activate")
async def activate_supply_route(route_name: str):
    """Activate a supply route"""
    for route in MOCK_SUPPLY_ROUTES:
        if route["name"] == route_name:
            route["active"] = True
            return {"message": f"Supply route {route_name} activated"}
    raise HTTPException(status_code=404, detail="Supply route not found")

@app.get("/api/fleet/operations", response_model=List[FleetOperation])
async def get_fleet_operations():
    """Get all fleet operations"""
    return MOCK_FLEET_OPERATIONS

@app.post("/api/fleet/operations")
async def create_fleet_operation(operation: FleetOperation):
    """Create a new fleet operation"""
    MOCK_FLEET_OPERATIONS.append(operation.dict())
    return {"message": "Fleet operation created successfully", "operation": operation}

@app.get("/api/fleet/status")
async def get_fleet_status():
    """Get overall fleet status"""
    total_ships = len(MOCK_SHIPS)
    active_ships = sum(1 for ship in MOCK_SHIPS if ship["nav"]["status"] in ["IN_ORBIT", "IN_TRANSIT"])
    active_operations = len([op for op in MOCK_FLEET_OPERATIONS if op["status"] == "active"])
    active_formations = len([f for f in MOCK_FORMATIONS if f["active"]])
    
    return {
        "total_ships": total_ships,
        "active_ships": active_ships,
        "docked_ships": total_ships - active_ships,
        "active_operations": active_operations,
        "active_formations": active_formations,
        "total_groups": len(MOCK_FLEET_GROUPS),
        "total_supply_routes": len([r for r in MOCK_SUPPLY_ROUTES if r["active"]])
    }

# Combat API Endpoints

@app.get("/api/fleet/combat/targets", response_model=List[CombatTarget])
async def get_combat_targets():
    """Get all combat targets"""
    return MOCK_COMBAT_TARGETS

@app.get("/api/fleet/combat/formations", response_model=List[CombatFormation])
async def get_combat_formations():
    """Get all combat formations"""
    return MOCK_COMBAT_FORMATIONS

@app.post("/api/fleet/combat/formations")
async def create_combat_formation(formation: CombatFormation):
    """Create a new combat formation"""
    MOCK_COMBAT_FORMATIONS.append(formation.dict())
    return {"message": "Combat formation created successfully", "formation": formation}

@app.post("/api/fleet/combat/attack")
async def initiate_combat(attack_data: dict):
    """Initiate coordinated attack"""
    attacking_ships = attack_data.get("ships", [])
    target_id = attack_data.get("target_id")
    tactics = attack_data.get("tactics", "alpha_strike")
    
    # Find target
    target = next((t for t in MOCK_COMBAT_TARGETS if t["target_id"] == target_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Calculate combat effectiveness
    ship_count = len(attacking_ships)
    combat_power = ship_count * 25  # Base combat power per ship
    
    # Apply tactics modifier
    tactics_modifiers = {
        "alpha_strike": 1.5,  # High damage, single coordinated attack
        "surround": 1.3,      # Tactical advantage
        "hit_and_run": 1.1,   # Safer but less effective
        "pincer": 1.4         # Two-pronged attack
    }
    
    final_power = combat_power * tactics_modifiers.get(tactics, 1.0)
    
    # Simulate combat result
    if final_power > target["estimated_health"]:
        result = "victory"
        target["estimated_health"] = 0
        damage_taken = max(0, target["threat_level"] * 10 - final_power // 2)
    else:
        result = "retreat"
        target["estimated_health"] -= final_power // 2
        damage_taken = target["threat_level"] * 15
    
    # Create combat operation
    combat_operation = {
        "operation_id": f"COMBAT_{len(MOCK_FLEET_OPERATIONS) + 1:03d}",
        "operation_type": "combat",
        "assigned_ships": attacking_ships,
        "target_location": target["location"],
        "status": "completed",
        "progress": {
            "result": result,
            "damage_dealt": final_power,
            "damage_taken": damage_taken,
            "tactics_used": tactics,
            "target_remaining_health": target["estimated_health"]
        },
        "estimated_completion": "2023-11-01T01:00:00.000Z"
    }
    
    MOCK_FLEET_OPERATIONS.append(combat_operation)
    
    return {
        "message": f"Combat initiated with {tactics} tactics",
        "result": result,
        "operation": combat_operation
    }

@app.post("/api/fleet/combat/coordinate")
async def coordinate_fleet_attack(coordination_data: dict):
    """Coordinate multi-ship attack with role assignments"""
    ships = coordination_data.get("ships", [])
    target_id = coordination_data.get("target_id")
    roles = coordination_data.get("roles", {})  # ship_symbol -> role
    formation_type = coordination_data.get("formation", "line")
    
    # Validate ships have combat capabilities
    combat_ships = []
    for ship_symbol in ships:
        ship = next((s for s in MOCK_SHIPS if s["symbol"] == ship_symbol), None)
        if ship and ship["registration"]["role"] in ["INTERCEPTOR", "PATROL", "COMMAND"]:
            combat_ships.append(ship_symbol)
    
    if not combat_ships:
        raise HTTPException(status_code=400, detail="No combat-capable ships selected")
    
    # Create formation and execute attack
    formation = CombatFormation(
        formation_id=f"CF_{len(MOCK_COMBAT_FORMATIONS) + 1:03d}",
        name=f"{formation_type.title()} Combat Formation",
        ships=combat_ships,
        roles=roles,
        target=target_id,
        tactics="coordinated_assault",
        status="engaging"
    )
    
    MOCK_COMBAT_FORMATIONS.append(formation.dict())
    
    # Execute coordinated attack
    attack_result = await initiate_combat({
        "ships": combat_ships,
        "target_id": target_id,
        "tactics": "coordinated_assault"
    })
    
    return {
        "message": "Coordinated attack executed",
        "formation": formation,
        "combat_result": attack_result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
