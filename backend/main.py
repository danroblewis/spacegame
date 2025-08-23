from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv
import asyncio
import json
from datetime import datetime, timedelta
import random
import math

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

class ScanResult(BaseModel):
    shipSymbol: str
    scanType: str
    timestamp: str
    data: dict
    cooldown: Optional[dict] = None

class SurveyRequest(BaseModel):
    shipSymbol: str

# New models for specialized operations
class SurveyRequest(BaseModel):
    pass  # Survey creation doesn't require a body

class ExtractRequest(BaseModel):
    survey: Optional[dict] = None  # Optional survey data

class SalvageOperationRequest(BaseModel):
    targetSymbol: str  # Target derelict ship or debris field

class ExplorationRequest(BaseModel):
    targetSystem: str  # System to explore/chart

class DiplomaticMissionRequest(BaseModel):
    ambassadorSymbol: str  # Ambassador cargo to transport
    destinationSymbol: str  # Diplomatic destination

class SearchRescueRequest(BaseModel):
    searchArea: str  # Area to search for lost ships/crew
    targetType: str  # "SHIP" or "CREW"

class EscortMissionRequest(BaseModel):
    protectedVesselSymbol: str  # Ship to protect
    routeWaypoints: List[str]  # Route waypoints to escort through

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

# New Pydantic models for automation
class AutoTradeConfig(BaseModel):
    ship_symbol: str
    enabled: bool
    min_profit_margin: float = 0.1
    max_trade_distance: int = 10
    preferred_goods: List[str] = []
    avoid_goods: List[str] = []

class RouteOptimization(BaseModel):
    ship_symbol: str
    destination: str
    optimize_for: str = "fuel_efficiency"  # "fuel_efficiency", "time", "profit"

class CombatAIConfig(BaseModel):
    ship_symbol: str
    enabled: bool
    aggression_level: str = "defensive"  # "passive", "defensive", "aggressive"
    retreat_threshold: float = 0.3
    target_priorities: List[str] = ["pirates", "hostiles"]

class MaintenanceSchedule(BaseModel):
    ship_symbol: str
    maintenance_type: str
    scheduled_time: datetime
    location: str
    priority: str = "medium"

class CrewRotationConfig(BaseModel):
    ship_symbol: str
    rotation_interval: int = 168  # hours
    min_morale_threshold: float = 0.7
    auto_hire: bool = True

class ResourceMonitoring(BaseModel):
    ship_symbol: str
    resource_type: str
    current_level: float
    optimal_level: float
    alert_threshold: float

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

# In-memory storage for automation configs (in production, use a database)
automation_configs = {
    "auto_trade": {},
    "combat_ai": {},
    "crew_rotation": {},
    "maintenance": [],
    "resource_monitoring": {}
}

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

# Mock scanning data
MOCK_SCAN_RESULTS = {
    "systems": [
        {
            "symbol": "X1-DF56",
            "sectorSymbol": "X1",
            "type": "RED_STAR",
            "x": 100,
            "y": -50,
            "distance": 150.2
        },
        {
            "symbol": "X1-DF57", 
            "sectorSymbol": "X1",
            "type": "NEUTRON_STAR",
            "x": -75,
            "y": 120,
            "distance": 95.8
        }
    ],
    "waypoints": [
        {
            "symbol": "X1-DF55-20250C",
            "type": "PLANET",
            "systemSymbol": "X1-DF55",
            "x": 45,
            "y": -80,
            "traits": [
                {"symbol": "VOLCANIC", "name": "Volcanic", "description": "Volcanic activity detected"},
                {"symbol": "RARE_METAL_DEPOSITS", "name": "Rare Metal Deposits", "description": "Contains valuable minerals"}
            ]
        },
        {
            "symbol": "X1-DF55-20250D",
            "type": "ASTEROID_FIELD",
            "systemSymbol": "X1-DF55", 
            "x": -120,
            "y": 60,
            "traits": [
                {"symbol": "COMMON_METAL_DEPOSITS", "name": "Common Metal Deposits", "description": "Standard mining resources"},
                {"symbol": "PRECIOUS_METAL_DEPOSITS", "name": "Precious Metal Deposits", "description": "Valuable precious metals detected"}
            ]
        }
    ],
    "ships": [
        {
            "symbol": "MERCHANT_VESSEL_001",
            "registration": {"factionSymbol": "COSMIC", "role": "TRADER"},
            "nav": {"waypointSymbol": "X1-DF55-20250Y", "status": "IN_ORBIT"},
            "frame": {"symbol": "FRAME_LIGHT_FREIGHTER"},
            "cargo": {"units": 75, "capacity": 100},
            "threat_level": "LOW",
            "distance": 25.5
        },
        {
            "symbol": "PATROL_SHIP_ALPHA",
            "registration": {"factionSymbol": "GALACTIC_EMPIRE", "role": "PATROL"}, 
            "nav": {"waypointSymbol": "X1-DF55-20250Z", "status": "IN_TRANSIT"},
            "frame": {"symbol": "FRAME_INTERCEPTOR"},
            "cargo": {"units": 10, "capacity": 20},
            "threat_level": "MEDIUM",
            "distance": 45.2
        }
    ]
}

MOCK_SURVEYS = [
    {
        "signature": "survey_001",
        "symbol": "X1-DF55-20250Y",
        "deposits": [
            {"symbol": "IRON_ORE", "name": "Iron Ore"},
            {"symbol": "COPPER_ORE", "name": "Copper Ore"},
            {"symbol": "ALUMINUM_ORE", "name": "Aluminum Ore"}
        ],
        "expiration": "2023-11-01T01:00:00.000Z",
        "size": "LARGE"
    },
    {
        "signature": "survey_002", 
        "symbol": "X1-DF55-20250B",
        "deposits": [
            {"symbol": "PRECIOUS_STONES", "name": "Precious Stones"},
            {"symbol": "RARE_EARTH_ELEMENTS", "name": "Rare Earth Elements"}
        ],
        "expiration": "2023-11-01T02:00:00.000Z",
        "size": "SMALL"
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

# Automation AI Endpoints

@app.get("/api/automation/status")
async def get_automation_status():
    """Get overall automation system status"""
    return {
        "auto_trading": {
            "active_ships": len(automation_configs["auto_trade"]),
            "total_trades_today": random.randint(10, 50),
            "profit_today": random.randint(5000, 25000)
        },
        "route_optimization": {
            "optimized_routes": random.randint(5, 15),
            "fuel_saved": random.randint(100, 500),
            "time_saved": random.randint(30, 120)
        },
        "combat_ai": {
            "active_ships": len(automation_configs["combat_ai"]),
            "threats_detected": random.randint(0, 3),
            "engagements_today": random.randint(0, 5)
        },
        "maintenance": {
            "scheduled_tasks": len(automation_configs["maintenance"]),
            "overdue_tasks": random.randint(0, 2),
            "efficiency_rating": round(random.uniform(0.85, 0.98), 2)
        },
        "crew_rotation": {
            "managed_ships": len(automation_configs["crew_rotation"]),
            "rotations_this_week": random.randint(2, 8),
            "average_morale": round(random.uniform(0.75, 0.95), 2)
        },
        "resource_monitoring": {
            "monitored_resources": len(automation_configs["resource_monitoring"]),
            "alerts_active": random.randint(0, 3),
            "optimization_suggestions": random.randint(1, 5)
        }
    }

# Auto-Trading Endpoints
@app.post("/api/automation/auto-trade/configure")
async def configure_auto_trade(config: AutoTradeConfig):
    """Configure auto-trading for a ship"""
    automation_configs["auto_trade"][config.ship_symbol] = config.dict()
    return {"message": f"Auto-trading configured for {config.ship_symbol}", "config": config}

@app.get("/api/automation/auto-trade/{ship_symbol}")
async def get_auto_trade_config(ship_symbol: str):
    """Get auto-trading configuration for a ship"""
    config = automation_configs["auto_trade"].get(ship_symbol)
    if not config:
        raise HTTPException(status_code=404, detail="Auto-trade config not found")
    return config

@app.get("/api/automation/auto-trade")
async def get_all_auto_trade_configs():
    """Get all auto-trading configurations"""
    return automation_configs["auto_trade"]

@app.get("/api/automation/market-analysis/{system_symbol}")
async def get_market_analysis(system_symbol: str):
    """Get AI-powered market analysis for auto-trading"""
    # Mock market analysis data
    analysis = {
        "system": system_symbol,
        "timestamp": datetime.now().isoformat(),
        "opportunities": [
            {
                "good": "IRON_ORE",
                "buy_location": f"{system_symbol}-MINE",
                "sell_location": f"{system_symbol}-STATION",
                "buy_price": 120,
                "sell_price": 180,
                "profit_margin": 0.5,
                "volume_available": 500,
                "risk_level": "low"
            },
            {
                "good": "FUEL",
                "buy_location": f"{system_symbol}-REFINERY",
                "sell_location": f"{system_symbol}-OUTPOST",
                "buy_price": 85,
                "sell_price": 110,
                "profit_margin": 0.29,
                "volume_available": 1000,
                "risk_level": "medium"
            }
        ],
        "market_trends": {
            "IRON_ORE": {"trend": "rising", "confidence": 0.85},
            "FUEL": {"trend": "stable", "confidence": 0.92},
            "ELECTRONICS": {"trend": "falling", "confidence": 0.78}
        },
        "recommendations": [
            "Focus on IRON_ORE trading for maximum profit",
            "FUEL markets are stable - good for consistent income",
            "Avoid ELECTRONICS until market stabilizes"
        ]
    }
    return analysis

# Route Optimization Endpoints
@app.post("/api/automation/route-optimization")
async def optimize_route(route_request: RouteOptimization):
    """Get AI-optimized route for a ship"""
    # Mock route optimization
    optimized_route = {
        "ship_symbol": route_request.ship_symbol,
        "destination": route_request.destination,
        "optimization_type": route_request.optimize_for,
        "waypoints": [
            {"symbol": "X1-DF55-20250X", "type": "PLANET", "fuel_cost": 15, "time_estimate": 45},
            {"symbol": "X1-DF55-20250Z", "type": "JUMP_GATE", "fuel_cost": 25, "time_estimate": 30},
            {"symbol": route_request.destination, "type": "DESTINATION", "fuel_cost": 20, "time_estimate": 60}
        ],
        "total_fuel_cost": 60,
        "total_time": 135,
        "efficiency_rating": 0.92,
        "alternative_routes": 3,
        "savings": {
            "fuel_saved": 15,
            "time_saved": 25,
            "credits_saved": 1200
        }
    }
    return optimized_route

# Combat AI Endpoints
@app.post("/api/automation/combat-ai/configure")
async def configure_combat_ai(config: CombatAIConfig):
    """Configure combat AI for a ship"""
    automation_configs["combat_ai"][config.ship_symbol] = config.dict()
    return {"message": f"Combat AI configured for {config.ship_symbol}", "config": config}

@app.get("/api/automation/combat-ai/{ship_symbol}")
async def get_combat_ai_config(ship_symbol: str):
    """Get combat AI configuration for a ship"""
    config = automation_configs["combat_ai"].get(ship_symbol)
    if not config:
        raise HTTPException(status_code=404, detail="Combat AI config not found")
    return config

@app.get("/api/automation/threat-assessment/{system_symbol}")
async def get_threat_assessment(system_symbol: str):
    """Get AI threat assessment for a system"""
    assessment = {
        "system": system_symbol,
        "threat_level": random.choice(["low", "medium", "high"]),
        "active_threats": [
            {
                "type": "pirate_patrol",
                "location": f"{system_symbol}-ASTEROID",
                "strength": "medium",
                "recommendation": "avoid_or_escort"
            }
        ],
        "safe_routes": [
            {"route": f"{system_symbol}-20250X to {system_symbol}-20250Z", "safety_rating": 0.95},
            {"route": f"{system_symbol}-20250Y to {system_symbol}-20250A", "safety_rating": 0.88}
        ],
        "patrol_schedule": {
            "next_patrol": "2024-01-15T14:30:00Z",
            "patrol_strength": "light"
        }
    }
    return assessment

# Maintenance Scheduling Endpoints
@app.post("/api/automation/maintenance/schedule")
async def schedule_maintenance(schedule: MaintenanceSchedule):
    """Schedule maintenance for a ship"""
    maintenance_task = schedule.dict()
    maintenance_task["id"] = f"maint_{len(automation_configs['maintenance'])}"
    automation_configs["maintenance"].append(maintenance_task)
    return {"message": "Maintenance scheduled", "task": maintenance_task}

@app.get("/api/automation/maintenance")
async def get_maintenance_schedule():
    """Get all scheduled maintenance tasks"""
    return automation_configs["maintenance"]

@app.get("/api/automation/maintenance/predictions/{ship_symbol}")
async def get_maintenance_predictions(ship_symbol: str):
    """Get predictive maintenance analysis for a ship"""
    predictions = {
        "ship_symbol": ship_symbol,
        "overall_health": round(random.uniform(0.75, 0.95), 2),
        "components": {
            "engine": {"health": 0.92, "next_maintenance": "7 days", "urgency": "low"},
            "hull": {"health": 0.88, "next_maintenance": "14 days", "urgency": "medium"},
            "reactor": {"health": 0.95, "next_maintenance": "21 days", "urgency": "low"},
            "life_support": {"health": 0.83, "next_maintenance": "10 days", "urgency": "medium"}
        },
        "recommendations": [
            "Schedule hull inspection within 2 weeks",
            "Monitor life support systems closely",
            "Engine performance is optimal"
        ],
        "cost_estimates": {
            "preventive": 5000,
            "if_delayed": 15000
        }
    }
    return predictions

# Crew Rotation Endpoints
@app.post("/api/automation/crew-rotation/configure")
async def configure_crew_rotation(config: CrewRotationConfig):
    """Configure automated crew rotation for a ship"""
    automation_configs["crew_rotation"][config.ship_symbol] = config.dict()
    return {"message": f"Crew rotation configured for {config.ship_symbol}", "config": config}

@app.get("/api/automation/crew-rotation/{ship_symbol}")
async def get_crew_rotation_config(ship_symbol: str):
    """Get crew rotation configuration for a ship"""
    config = automation_configs["crew_rotation"].get(ship_symbol)
    if not config:
        raise HTTPException(status_code=404, detail="Crew rotation config not found")
    return config

@app.get("/api/automation/crew-analysis/{ship_symbol}")
async def get_crew_analysis(ship_symbol: str):
    """Get AI crew performance analysis"""
    analysis = {
        "ship_symbol": ship_symbol,
        "crew_size": random.randint(2, 8),
        "morale": round(random.uniform(0.65, 0.95), 2),
        "efficiency": round(random.uniform(0.70, 0.98), 2),
        "fatigue_level": round(random.uniform(0.10, 0.80), 2),
        "crew_members": [
            {
                "name": "Captain Sarah Chen",
                "role": "Commander",
                "morale": 0.92,
                "efficiency": 0.95,
                "days_since_rotation": 45,
                "recommendation": "excellent_performance"
            },
            {
                "name": "Engineer Rodriguez",
                "role": "Engineer",
                "morale": 0.78,
                "efficiency": 0.88,
                "days_since_rotation": 67,
                "recommendation": "schedule_rotation_soon"
            }
        ],
        "recommendations": [
            "Schedule rotation for Engineer Rodriguez",
            "Consider bonus for high-performing crew",
            "Overall crew performance is above average"
        ]
    }
    return analysis

# Resource Monitoring Endpoints
@app.get("/api/automation/resource-monitoring")
async def get_resource_monitoring():
    """Get all resource monitoring configurations"""
    return automation_configs["resource_monitoring"]

@app.post("/api/automation/resource-monitoring/configure")
async def configure_resource_monitoring(config: ResourceMonitoring):
    """Configure resource monitoring for a ship"""
    key = f"{config.ship_symbol}_{config.resource_type}"
    automation_configs["resource_monitoring"][key] = config.dict()
    return {"message": "Resource monitoring configured", "config": config}

@app.get("/api/automation/resource-optimization/{ship_symbol}")
async def get_resource_optimization(ship_symbol: str):
    """Get AI resource optimization recommendations"""
    optimization = {
        "ship_symbol": ship_symbol,
        "timestamp": datetime.now().isoformat(),
        "resources": {
            "fuel": {
                "current": 450,
                "optimal": 500,
                "status": "good",
                "recommendation": "top_off_at_next_station"
            },
            "food": {
                "current": 80,
                "optimal": 120,
                "status": "low",
                "recommendation": "restock_immediately"
            },
            "water": {
                "current": 200,
                "optimal": 180,
                "status": "excess",
                "recommendation": "consider_selling_surplus"
            }
        },
        "efficiency_score": 0.87,
        "cost_savings": {
            "weekly": 2500,
            "monthly": 10000
        },
        "alerts": [
            "Food supplies below optimal level",
            "Fuel efficiency could be improved by 8%"
        ]
    }
    return optimization


@app.post("/api/ships/{ship_symbol}/survey")
async def create_survey(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Create a survey of extractable resources at current location"""
    if not HAS_VALID_TOKEN:
        # Mock survey response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Mock survey data for asteroid field
        current_waypoint = mock_ship["nav"]["waypointSymbol"]
        if "20250Y" in current_waypoint:  # Asteroid field
            mock_survey = {
                "signature": f"survey-{current_waypoint}-{ship_symbol}",
                "symbol": current_waypoint,
                "deposits": [
                    {"symbol": "IRON_ORE"},
                    {"symbol": "COPPER_ORE"},
                    {"symbol": "PRECIOUS_STONES"}
                ],
                "expiration": "2024-01-01T12:00:00Z",
                "size": "MODERATE"
            }
            return {
                "data": {
                    "cooldown": {"shipSymbol": ship_symbol, "totalSeconds": 60, "remainingSeconds": 60},
                    "surveys": [mock_survey]
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Cannot survey at this location")
# Scanning and Intelligence Endpoints

@app.post("/api/ships/{ship_symbol}/scan/systems")
async def scan_systems(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Long-range sensors - Detect systems and celestial objects"""
    if not HAS_VALID_TOKEN:
        # Mock response for demo
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
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/scan/systems", headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/scan/waypoints")
async def scan_waypoints(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Planetary survey - Scan waypoints for resources and composition"""
    if not HAS_VALID_TOKEN:
        # Mock response for demo
        return {
            "data": {
                "cooldown": {
                    "shipSymbol": ship_symbol,
                    "totalSeconds": 60,
                    "remainingSeconds": 60,
                    "expiration": "2023-11-01T00:01:00.000Z"
                },
                "waypoints": MOCK_SCAN_RESULTS["waypoints"]
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/scan/waypoints", headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/scan/ships")
async def scan_ships(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Signal interception and threat assessment - Scan nearby ships"""
    if not HAS_VALID_TOKEN:
        # Mock response for demo
        return {
            "data": {
                "cooldown": {
                    "shipSymbol": ship_symbol,
                    "totalSeconds": 10,
                    "remainingSeconds": 10,
                    "expiration": "2023-11-01T00:00:10.000Z"
                },
                "ships": MOCK_SCAN_RESULTS["ships"]
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/scan/ships", headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/survey")
async def create_survey(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Resource mapping - Create detailed survey of current waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock response for demo
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
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/survey", headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/extract")
async def extract_resources(ship_symbol: str, request: ExtractRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Extract resources from current location"""
    if not HAS_VALID_TOKEN:
        # Mock extraction response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        current_waypoint = mock_ship["nav"]["waypointSymbol"]
        if "20250Y" in current_waypoint:  # Asteroid field
            extracted_resource = "IRON_ORE"
            extracted_units = 5
            
            # Add to ship cargo
            cargo_item = next((item for item in mock_ship["cargo"]["inventory"] if item["symbol"] == extracted_resource), None)
            if cargo_item:
                cargo_item["units"] += extracted_units
            else:
                mock_ship["cargo"]["inventory"].append({"symbol": extracted_resource, "units": extracted_units})
            
            mock_ship["cargo"]["units"] += extracted_units
            
            return {
                "data": {
                    "extraction": {
                        "shipSymbol": ship_symbol,
                        "yield": {"symbol": extracted_resource, "units": extracted_units}
                    },
                    "cooldown": {"shipSymbol": ship_symbol, "totalSeconds": 90, "remainingSeconds": 90},
                    "cargo": mock_ship["cargo"],
                    "events": []
                }
            }
        else:
            raise HTTPException(status_code=400, detail="Cannot extract resources at this location")
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {}
        if request.survey:
            payload["survey"] = request.survey
        
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/extract", 
                                   json=payload, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ships/{ship_symbol}/cooldown")
async def get_ship_cooldown(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get current ship cooldown status"""
    if not HAS_VALID_TOKEN:
        # Mock response - no cooldown
        return {
            "data": {
                "shipSymbol": ship_symbol,
                "totalSeconds": 0,
                "remainingSeconds": 0,
                "expiration": None
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/cooldown", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            # No cooldown
            return {
                "data": {
                    "shipSymbol": ship_symbol,
                    "totalSeconds": 0,
                    "remainingSeconds": 0,
                    "expiration": None
                }
            }
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/ships/{ship_symbol}/salvage")
async def salvage_operation(ship_symbol: str, request: SalvageOperationRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Perform salvage operation on derelict ships or debris"""
    if not HAS_VALID_TOKEN:
        # Mock salvage response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Mock salvage results
        salvaged_items = [
            {"symbol": "SCRAP_METAL", "units": 10},
            {"symbol": "ADVANCED_CIRCUITRY", "units": 2}
        ]
        
        for item in salvaged_items:
            cargo_item = next((c for c in mock_ship["cargo"]["inventory"] if c["symbol"] == item["symbol"]), None)
            if cargo_item:
                cargo_item["units"] += item["units"]
            else:
                mock_ship["cargo"]["inventory"].append(item)
        
        mock_ship["cargo"]["units"] += sum(item["units"] for item in salvaged_items)
        
        return {
            "data": {
                "salvage": {"shipSymbol": ship_symbol, "items": salvaged_items},
                "cargo": mock_ship["cargo"],
                "cooldown": {"shipSymbol": ship_symbol, "totalSeconds": 120, "remainingSeconds": 120}
            }
        }
    
    # For real API, this would be a custom operation not directly supported by SpaceTraders
    # We'd need to implement it using existing endpoints or wait for official support
    raise HTTPException(status_code=501, detail="Salvage operations not yet implemented with real API")

@app.post("/api/ships/{ship_symbol}/explore")
async def exploration_mission(ship_symbol: str, request: ExplorationRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Perform exploration/charting of unknown systems"""
    if not HAS_VALID_TOKEN:
        # Mock exploration response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Mock exploration results - discovering new waypoints/systems
        exploration_results = {
            "systemSymbol": request.targetSystem,
            "newWaypoints": [
                {"symbol": f"{request.targetSystem}-NEW1", "type": "ASTEROID_FIELD", "x": 100, "y": 50},
                {"symbol": f"{request.targetSystem}-NEW2", "type": "PLANET", "x": -80, "y": 120}
            ],
            "chartingProgress": 75  # Percentage of system charted
        }
        
        return {
            "data": {
                "exploration": exploration_results,
                "cooldown": {"shipSymbol": ship_symbol, "totalSeconds": 180, "remainingSeconds": 180}
            }
        }
    
    raise HTTPException(status_code=501, detail="Exploration missions not yet implemented with real API")

@app.post("/api/ships/{ship_symbol}/diplomatic-mission")
async def diplomatic_mission(ship_symbol: str, request: DiplomaticMissionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Transport ambassadors or perform diplomatic missions"""
    if not HAS_VALID_TOKEN:
        # Mock diplomatic mission response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Check if ship has the ambassador cargo
        ambassador_cargo = next((item for item in mock_ship["cargo"]["inventory"] 
                               if item["symbol"] == request.ambassadorSymbol), None)
        if not ambassador_cargo:
            raise HTTPException(status_code=400, detail="Ambassador not found in cargo")
        
        return {
            "data": {
                "mission": {
                    "type": "DIPLOMATIC",
                    "ambassador": request.ambassadorSymbol,
                    "destination": request.destinationSymbol,
                    "status": "IN_PROGRESS",
                    "diplomatic_bonus": 1000  # Credits reward
                },
                "cooldown": {"shipSymbol": ship_symbol, "totalSeconds": 300, "remainingSeconds": 300}
            }
        }
    
    raise HTTPException(status_code=501, detail="Diplomatic missions not yet implemented with real API")

@app.post("/api/ships/{ship_symbol}/search-rescue")
async def search_rescue_mission(ship_symbol: str, request: SearchRescueRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Search for lost ships or rescue crew members"""
    if not HAS_VALID_TOKEN:
        # Mock search and rescue response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Mock search results
        import random
        success = random.random() > 0.3  # 70% chance of finding something
        
        if success:
            if request.targetType == "SHIP":
                result = {
                    "found": "DERELICT_SHIP",
                    "location": request.searchArea,
                    "salvage_value": 5000,
                    "rescue_bonus": 2000
                }
            else:  # CREW
                result = {
                    "found": "CREW_POD",
                    "survivors": 3,
                    "rescue_bonus": 1500
                }
        else:
            result = {"found": None, "search_exhausted": True}
        
        return {
            "data": {
                "search_rescue": result,
                "cooldown": {"shipSymbol": ship_symbol, "totalSeconds": 240, "remainingSeconds": 240}
            }
        }
    
    raise HTTPException(status_code=501, detail="Search and rescue missions not yet implemented with real API")

@app.post("/api/ships/{ship_symbol}/escort")
async def escort_mission(ship_symbol: str, request: EscortMissionRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Escort other vessels through dangerous routes"""
    if not HAS_VALID_TOKEN:
        # Mock escort mission response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        return {
            "data": {
                "escort": {
                    "protectedVessel": request.protectedVesselSymbol,
                    "route": request.routeWaypoints,
                    "status": "ESCORTING",
                    "currentWaypoint": 0,
                    "escort_fee": 3000  # Credits reward
                },
                "cooldown": {"shipSymbol": ship_symbol, "totalSeconds": 60, "remainingSeconds": 60}
            }
        }
    
    raise HTTPException(status_code=501, detail="Escort missions not yet implemented with real API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
