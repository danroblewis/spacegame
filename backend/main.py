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

class RefuelRequest(BaseModel):
    units: Optional[int] = None

class HireCrewRequest(BaseModel):
    hireableCrewId: str

class TransferRequest(BaseModel):
    tradeSymbol: str
    units: int
    shipSymbol: str

# Security & Stealth Action Models
class SecurityActionRequest(BaseModel):
    action: str  # "activate" or "deactivate"
    duration: Optional[int] = None  # Duration in seconds for timed actions

class SecurityStatus(BaseModel):
    cloakingActive: bool = False
    cloakingCooldown: Optional[int] = None
    stealthModeActive: bool = False 
    stealthModeLevel: int = 0  # 0-3 stealth levels
    signalJammingActive: bool = False
    jammingRadius: int = 0  # Jamming radius in units
    electronicWarfareActive: bool = False
    countermeasuresActive: bool = False
    countermeasuresCharges: int = 3  # Available countermeasure charges
    encryptionActive: bool = False
    encryptionLevel: int = 1  # 1-5 encryption levels
    energyConsumption: int = 0  # Current energy drain from security systems

# Global security status storage (in production, this would be in a database)
ship_security_status = {}

# Mock data for testing
MOCK_AVAILABLE_CREW = [
    {
        "id": "hire_001",
        "name": "Marcus Thompson",
        "role": "GUNNER",
        "level": 2,
        "skills": {"combat": 70, "weapons": 75, "tactics": 60},
        "salary": 100
    },
    {
        "id": "hire_002",
        "name": "Dr. Elena Vasquez",
        "role": "MEDIC",
        "level": 3,
        "skills": {"medicine": 85, "surgery": 80, "biology": 70},
        "salary": 130
    },
    {
        "id": "hire_003",
        "name": "Jake Morrison",
        "role": "MINER",
        "level": 3,
        "skills": {"mining": 80, "geology": 75, "equipment": 70},
        "salary": 110
    },
    {
        "id": "hire_004",
        "name": "Security Chief Rivera",
        "role": "SECURITY",
        "level": 4,
        "skills": {"security": 90, "combat": 85, "investigation": 75},
        "salary": 140
    }
]
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

# Resource Management Models
class ResourceData(BaseModel):
    fuel: dict
    power: dict
    heat: dict
    life_support: dict
    waste: dict
    emergency: dict

class ResourceAction(BaseModel):
    action: str
    parameters: dict = {}

# Mock resource data generator
def generate_mock_resource_data(ship_symbol: str):
    import random
    return {
        "fuel": {
            "current": random.randint(70, 100),
            "capacity": 100,
            "efficiency": random.randint(85, 98),
            "consumption_rate": round(random.uniform(0.8, 1.5), 1)
        },
        "power": {
            "current": random.randint(75, 95),
            "capacity": 100,
            "distribution": {
                "engines": random.randint(30, 40),
                "life_support": random.randint(20, 30),
                "systems": random.randint(15, 25),
                "shields": random.randint(10, 20)
            }
        },
        "heat": {
            "current": random.randint(30, 60),
            "max_safe": 80,
            "dissipation_rate": round(random.uniform(1.8, 2.5), 1),
            "thermal_vents": random.randint(3, 6)
        },
        "life_support": {
            "oxygen": random.randint(90, 100),
            "temperature": random.randint(20, 24),
            "humidity": random.randint(40, 55),
            "crew_comfort": random.randint(75, 95),
            "air_quality": random.randint(85, 100)
        },
        "waste": {
            "organic": random.randint(5, 15),
            "recyclable": random.randint(3, 12),
            "hazardous": random.randint(1, 5),
            "recycling_efficiency": random.randint(70, 85),
            "storage_capacity": 50
        },
        "emergency": {
            "medical": random.randint(80, 100),
            "rations": random.randint(70, 95),
            "oxygen_backup": random.randint(85, 100),
            "repair_kits": random.randint(2, 5),
            "emergency_beacon": True
        }
    }

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

@app.get("/api/ships/{ship_symbol}/resources")
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

@app.post("/api/ships/{ship_symbol}/resources/{action}")
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

@app.get("/api/ships/{ship_symbol}/resource-efficiency")
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

@app.post("/api/ships/{ship_symbol}/emergency-protocol")
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

@app.post("/api/ships/{ship_symbol}/refuel")
async def refuel_ship(ship_symbol: str, request: RefuelRequest = RefuelRequest(), client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Refuel ship at current waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock refuel response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        if mock_ship["nav"]["status"] != "DOCKED":
            raise HTTPException(status_code=400, detail="Ship must be docked to refuel")
        
        # Mock fuel update
        fuel_cost = 50 if request.units is None else request.units
        fuel_units = 100 if request.units is None else min(request.units, 100)
        
        return {
            "data": {
                "agent": {"credits": 999950},
                "fuel": {"current": fuel_units, "capacity": 100, "consumed": {"amount": 0, "timestamp": "2023-11-01T00:00:00.000Z"}},
                "transaction": {"waypointSymbol": mock_ship["nav"]["waypointSymbol"], "shipSymbol": ship_symbol, "tradeSymbol": "FUEL", "type": "PURCHASE", "units": fuel_units, "pricePerUnit": 1, "totalPrice": fuel_cost, "timestamp": "2023-11-01T00:00:00.000Z"}
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {}
        if request.units is not None:
            payload["units"] = request.units
            
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/refuel", 
                                   json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ships/{ship_symbol}/repair")
async def get_repair_cost(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get repair cost for ship"""
    if not HAS_VALID_TOKEN:
        # Mock repair cost response
        return {
            "data": {
                "transaction": {
                    "waypointSymbol": "X1-DF55-20250X",
                    "shipSymbol": ship_symbol,
                    "totalPrice": 100,
                    "timestamp": "2023-11-01T00:00:00.000Z"
                }
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/repair", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/repair")
async def repair_ship(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Repair ship at current waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock repair response
        return {
            "data": {
                "agent": {"credits": 999900},
                "transaction": {
                    "waypointSymbol": "X1-DF55-20250X",
                    "shipSymbol": ship_symbol,
                    "totalPrice": 100,
                    "timestamp": "2023-11-01T00:00:00.000Z"
                }
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/repair", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ships/{ship_symbol}/crew")
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

@app.post("/api/ships/{ship_symbol}/crew/hire")
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

@app.get("/api/crew/available")
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

@app.post("/api/ships/{ship_symbol}/crew/{crew_symbol}/dismiss")
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

@app.post("/api/ships/{ship_symbol}/transfer")
async def transfer_cargo(ship_symbol: str, request: TransferRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Transfer cargo between ships"""
    if not HAS_VALID_TOKEN:
        # Mock transfer response
        source_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        target_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == request.shipSymbol), None)
        
        if not source_ship or not target_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Mock cargo transfer logic
        source_item = next((item for item in source_ship["cargo"]["inventory"] if item["symbol"] == request.tradeSymbol), None)
        if not source_item or source_item["units"] < request.units:
            raise HTTPException(status_code=400, detail="Insufficient cargo")
        
        # Update mock cargo
        source_item["units"] -= request.units
        if source_item["units"] == 0:
            source_ship["cargo"]["inventory"].remove(source_item)
        
        target_item = next((item for item in target_ship["cargo"]["inventory"] if item["symbol"] == request.tradeSymbol), None)
        if target_item:
            target_item["units"] += request.units
        else:
            target_ship["cargo"]["inventory"].append({"symbol": request.tradeSymbol, "units": request.units})
        
        return {
            "data": {
                "cargo": source_ship["cargo"]
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {
            "tradeSymbol": request.tradeSymbol,
            "units": request.units,
            "shipSymbol": request.shipSymbol
        }
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/transfer", 
                                   json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Security & Stealth Action Endpoints

@app.get("/api/ships/{ship_symbol}/security/status", response_model=SecurityStatus)
async def get_ship_security_status(ship_symbol: str):
    """Get current security status for a ship"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    return ship_security_status[ship_symbol]

@app.post("/api/ships/{ship_symbol}/security/cloaking")
async def toggle_cloaking_device(ship_symbol: str, request: SecurityActionRequest):
    """Activate or deactivate cloaking device"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    
    status = ship_security_status[ship_symbol]
    
    if request.action == "activate":
        if status.cloakingCooldown and status.cloakingCooldown > 0:
            raise HTTPException(status_code=400, detail="Cloaking device is on cooldown")
        
        status.cloakingActive = True
        status.energyConsumption += 25
        status.cloakingCooldown = None
        
        return {
            "message": "Cloaking device activated. Ship is now hidden from sensors.",
            "status": status,
            "effectDuration": request.duration or 300  # 5 minutes default
        }
    
    elif request.action == "deactivate":
        status.cloakingActive = False
        status.energyConsumption = max(0, status.energyConsumption - 25)
        status.cloakingCooldown = 120  # 2 minute cooldown
        
        return {
            "message": "Cloaking device deactivated. Ship is now visible to sensors.",
            "status": status,
            "cooldownDuration": 120
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'activate' or 'deactivate'")

@app.post("/api/ships/{ship_symbol}/security/jamming")
async def toggle_signal_jamming(ship_symbol: str, request: SecurityActionRequest):
    """Activate or deactivate signal jamming"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    
    status = ship_security_status[ship_symbol]
    
    if request.action == "activate":
        status.signalJammingActive = True
        status.jammingRadius = 50  # 50 unit radius
        status.energyConsumption += 15
        
        return {
            "message": "Signal jamming activated. Disrupting enemy communications in 50 unit radius.",
            "status": status,
            "jammingRadius": 50
        }
    
    elif request.action == "deactivate":
        status.signalJammingActive = False
        status.jammingRadius = 0
        status.energyConsumption = max(0, status.energyConsumption - 15)
        
        return {
            "message": "Signal jamming deactivated.",
            "status": status
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'activate' or 'deactivate'")

@app.post("/api/ships/{ship_symbol}/security/electronic-warfare")
async def toggle_electronic_warfare(ship_symbol: str, request: SecurityActionRequest):
    """Activate or deactivate electronic warfare systems"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    
    status = ship_security_status[ship_symbol]
    
    if request.action == "activate":
        status.electronicWarfareActive = True
        status.energyConsumption += 30
        
        return {
            "message": "Electronic warfare systems activated. Ready to hack enemy systems.",
            "status": status,
            "capabilities": ["System infiltration", "Data extraction", "Remote control override"]
        }
    
    elif request.action == "deactivate":
        status.electronicWarfareActive = False
        status.energyConsumption = max(0, status.energyConsumption - 30)
        
        return {
            "message": "Electronic warfare systems deactivated.",
            "status": status
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'activate' or 'deactivate'")

@app.post("/api/ships/{ship_symbol}/security/stealth-mode")
async def toggle_stealth_mode(ship_symbol: str, request: SecurityActionRequest):
    """Activate or deactivate stealth mode"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    
    status = ship_security_status[ship_symbol]
    
    if request.action == "activate":
        status.stealthModeActive = True
        status.stealthModeLevel = min(3, status.stealthModeLevel + 1)
        status.energyConsumption += 10 * status.stealthModeLevel
        
        return {
            "message": f"Stealth mode activated at level {status.stealthModeLevel}. Sensor signature reduced.",
            "status": status,
            "signatureReduction": f"{25 * status.stealthModeLevel}%"
        }
    
    elif request.action == "deactivate":
        if status.stealthModeActive:
            status.energyConsumption = max(0, status.energyConsumption - (10 * status.stealthModeLevel))
        status.stealthModeActive = False
        status.stealthModeLevel = 0
        
        return {
            "message": "Stealth mode deactivated. Sensor signature at normal levels.",
            "status": status
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'activate' or 'deactivate'")

@app.post("/api/ships/{ship_symbol}/security/countermeasures")
async def deploy_countermeasures(ship_symbol: str, request: SecurityActionRequest):
    """Deploy countermeasures (decoys and chaff)"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    
    status = ship_security_status[ship_symbol]
    
    if request.action == "activate":
        if status.countermeasuresCharges <= 0:
            raise HTTPException(status_code=400, detail="No countermeasure charges remaining")
        
        status.countermeasuresActive = True
        status.countermeasuresCharges -= 1
        
        return {
            "message": "Countermeasures deployed! Decoys and chaff active.",
            "status": status,
            "remainingCharges": status.countermeasuresCharges,
            "effectDuration": 180  # 3 minutes
        }
    
    elif request.action == "deactivate":
        status.countermeasuresActive = False
        
        return {
            "message": "Countermeasures deactivated.",
            "status": status
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'activate' or 'deactivate'")

@app.post("/api/ships/{ship_symbol}/security/encryption")
async def toggle_encryption(ship_symbol: str, request: SecurityActionRequest):
    """Activate or deactivate secure communications encryption"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    
    status = ship_security_status[ship_symbol]
    
    if request.action == "activate":
        status.encryptionActive = True
        status.encryptionLevel = min(5, status.encryptionLevel + 1)
        status.energyConsumption += 5 * status.encryptionLevel
        
        return {
            "message": f"Encryption activated at level {status.encryptionLevel}. Communications secured.",
            "status": status,
            "encryptionStrength": f"AES-{128 + (status.encryptionLevel * 64)}"
        }
    
    elif request.action == "deactivate":
        if status.encryptionActive:
            status.energyConsumption = max(0, status.energyConsumption - (5 * status.encryptionLevel))
        status.encryptionActive = False
        status.encryptionLevel = 1
        
        return {
            "message": "Encryption deactivated. Communications are now unsecured.",
            "status": status
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'activate' or 'deactivate'")

@app.post("/api/ships/{ship_symbol}/security/recharge-countermeasures")
async def recharge_countermeasures(ship_symbol: str):
    """Recharge countermeasure charges (simulates restocking at a station)"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    
    status = ship_security_status[ship_symbol]
    status.countermeasuresCharges = 3  # Full recharge
    
    return {
        "message": "Countermeasure charges recharged to maximum capacity.",
        "status": status,
        "totalCharges": 3
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
