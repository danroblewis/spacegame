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

# Specialized Operations Endpoints

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
