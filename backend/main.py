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

# Add new Pydantic models for cargo operations before line 78
class CargoOperationRequest(BaseModel):
    symbol: str
    units: int

class JettisonRequest(BaseModel):
    symbol: str
    units: int

class TransferCargoRequest(BaseModel):
    symbol: str
    units: int
    destination: str  # Ship symbol to transfer to

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

@app.get("/api/ships/{ship_symbol}/cargo")
async def get_ship_cargo(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get cargo details for a specific ship"""
    if not HAS_VALID_TOKEN:
        # Mock cargo response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        return {"data": mock_ship["cargo"]}
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/cargo", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/purchase")
async def purchase_cargo(ship_symbol: str, request: CargoOperationRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Purchase cargo for a ship from the local market"""
    if not HAS_VALID_TOKEN:
        # Mock purchase response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Check cargo capacity
        current_cargo = mock_ship["cargo"]["units"]
        cargo_capacity = mock_ship["cargo"]["capacity"]
        
        if current_cargo + request.units > cargo_capacity:
            raise HTTPException(status_code=400, detail="Insufficient cargo capacity")
        
        # Add to inventory or update existing item
        existing_item = next((item for item in mock_ship["cargo"]["inventory"] if item["symbol"] == request.symbol), None)
        if existing_item:
            existing_item["units"] += request.units
        else:
            mock_ship["cargo"]["inventory"].append({
                "symbol": request.symbol,
                "name": request.symbol.replace("_", " ").title(),
                "description": f"A unit of {request.symbol}",
                "units": request.units
            })
        
        mock_ship["cargo"]["units"] += request.units
        
        # Mock transaction data
        return {
            "data": {
                "agent": {"symbol": "DEMO_AGENT", "credits": 999000},  # Reduced credits
                "cargo": mock_ship["cargo"],
                "transaction": {
                    "symbol": request.symbol,
                    "type": "PURCHASE",
                    "units": request.units,
                    "pricePerUnit": 100,  # Mock price
                    "totalPrice": request.units * 100,
                    "timestamp": "2023-11-01T00:00:00.000Z"
                }
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {"symbol": request.symbol, "units": request.units}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/purchase", 
                                   json=payload, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/sell")
async def sell_cargo(ship_symbol: str, request: CargoOperationRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Sell cargo from a ship to the local market"""
    if not HAS_VALID_TOKEN:
        # Mock sell response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Find and remove/reduce item from inventory
        existing_item = next((item for item in mock_ship["cargo"]["inventory"] if item["symbol"] == request.symbol), None)
        if not existing_item:
            raise HTTPException(status_code=400, detail="Item not found in cargo")
        
        if existing_item["units"] < request.units:
            raise HTTPException(status_code=400, detail="Insufficient units to sell")
        
        existing_item["units"] -= request.units
        mock_ship["cargo"]["units"] -= request.units
        
        # Remove item if no units left
        if existing_item["units"] <= 0:
            mock_ship["cargo"]["inventory"].remove(existing_item)
        
        return {
            "data": {
                "agent": {"symbol": "DEMO_AGENT", "credits": 1001000},  # Increased credits
                "cargo": mock_ship["cargo"],
                "transaction": {
                    "symbol": request.symbol,
                    "type": "SELL",
                    "units": request.units,
                    "pricePerUnit": 120,  # Mock sell price (higher than purchase)
                    "totalPrice": request.units * 120,
                    "timestamp": "2023-11-01T00:00:00.000Z"
                }
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {"symbol": request.symbol, "units": request.units}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/sell", 
                                   json=payload, headers=headers)
        
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/jettison")
async def jettison_cargo(ship_symbol: str, request: JettisonRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Jettison cargo from a ship (emergency dump)"""
    if not HAS_VALID_TOKEN:
        # Mock jettison response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Find and remove/reduce item from inventory
        existing_item = next((item for item in mock_ship["cargo"]["inventory"] if item["symbol"] == request.symbol), None)
        if not existing_item:
            raise HTTPException(status_code=400, detail="Item not found in cargo")
        
        if existing_item["units"] < request.units:
            raise HTTPException(status_code=400, detail="Insufficient units to jettison")
        
        existing_item["units"] -= request.units
        mock_ship["cargo"]["units"] -= request.units
        
        # Remove item if no units left
        if existing_item["units"] <= 0:
            mock_ship["cargo"]["inventory"].remove(existing_item)
        
        return {
            "data": {
                "cargo": mock_ship["cargo"]
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {"symbol": request.symbol, "units": request.units}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/jettison", 
                                   json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/transfer")
async def transfer_cargo(ship_symbol: str, request: TransferCargoRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Transfer cargo between ships"""
    if not HAS_VALID_TOKEN:
        # Mock transfer response
        source_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not source_ship:
            raise HTTPException(status_code=404, detail="Source ship not found")
        
        # For demo, we'll just update the source ship (destination ship logic would be more complex)
        existing_item = next((item for item in source_ship["cargo"]["inventory"] if item["symbol"] == request.symbol), None)
        if not existing_item:
            raise HTTPException(status_code=400, detail="Item not found in cargo")
        
        if existing_item["units"] < request.units:
            raise HTTPException(status_code=400, detail="Insufficient units to transfer")
        
        existing_item["units"] -= request.units
        source_ship["cargo"]["units"] -= request.units
        
        # Remove item if no units left
        if existing_item["units"] <= 0:
            source_ship["cargo"]["inventory"].remove(existing_item)
        
        return {
            "data": {
                "cargo": source_ship["cargo"]
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = {"symbol": request.symbol, "units": request.units}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/transfer", 
                                   json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/systems/{system_symbol}/waypoints/{waypoint_symbol}/market")
async def get_market(system_symbol: str, waypoint_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get market information for a waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock market data
        if waypoint_symbol == "X1-DF55-20250X":
            return {
                "data": {
                    "symbol": waypoint_symbol,
                    "exports": [
                        {"symbol": "FOOD", "name": "Food", "description": "Basic food supplies"},
                        {"symbol": "FUEL", "name": "Fuel", "description": "Ship fuel"}
                    ],
                    "imports": [
                        {"symbol": "METAL_ORE", "name": "Metal Ore", "description": "Raw metal ore"},
                        {"symbol": "RARE_METALS", "name": "Rare Metals", "description": "Precious metals"}
                    ],
                    "exchange": [
                        {"symbol": "EQUIPMENT", "name": "Equipment", "description": "General equipment"}
                    ],
                    "tradeGoods": [
                        {
                            "symbol": "FOOD",
                            "name": "Food",
                            "description": "Basic food supplies",
                            "tradeVolume": 100,
                            "supply": "ABUNDANT",
                            "purchasePrice": 95,
                            "sellPrice": 105
                        },
                        {
                            "symbol": "FUEL",
                            "name": "Fuel", 
                            "description": "Ship fuel",
                            "tradeVolume": 200,
                            "supply": "HIGH",
                            "purchasePrice": 80,
                            "sellPrice": 90
                        },
                        {
                            "symbol": "METAL_ORE",
                            "name": "Metal Ore",
                            "description": "Raw metal ore",
                            "tradeVolume": 50,
                            "supply": "SCARCE",
                            "purchasePrice": 150,
                            "sellPrice": 160
                        }
                    ]
                }
            }
        else:
            raise HTTPException(status_code=404, detail="Market not found")
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/systems/{system_symbol}/waypoints/{waypoint_symbol}/market", 
                                  headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/cargo/optimize")
async def optimize_cargo(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Optimize cargo arrangement for maximum efficiency"""
    if not HAS_VALID_TOKEN:
        # Mock optimization response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Simulate cargo optimization by sorting by value density
        if mock_ship["cargo"]["inventory"]:
            mock_ship["cargo"]["inventory"].sort(key=lambda x: x["units"], reverse=True)
        
        return {
            "data": {
                "cargo": mock_ship["cargo"],
                "optimization": {
                    "efficiency_improvement": "15%",
                    "space_saved": 5,
                    "value_density_optimized": True,
                    "recommendations": [
                        "High-value items moved to secure compartments",
                        "Bulk goods consolidated",
                        "Emergency supplies positioned for quick access"
                    ]
                }
            }
        }
    
    # For real API, this would call SpaceTraders optimization endpoints
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/cargo/optimize", 
                                   headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/cargo/scan")
async def scan_cargo(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Perform detailed cargo scanning and analysis"""
    if not HAS_VALID_TOKEN:
        # Mock scan response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        cargo = mock_ship["cargo"]
        total_value = sum(item["units"] * 100 for item in cargo["inventory"])
        efficiency = round((cargo["units"] / cargo["capacity"]) * 100)
        
        return {
            "data": {
                "scan_results": {
                    "total_items": len(cargo["inventory"]),
                    "total_units": cargo["units"],
                    "capacity_used": efficiency,
                    "estimated_value": total_value,
                    "cargo_integrity": "98%",
                    "contraband_detected": False,
                    "hidden_compartments": 0,
                    "item_analysis": [
                        {
                            "symbol": item["symbol"],
                            "units": item["units"],
                            "condition": "Good",
                            "market_value": item["units"] * 100,
                            "rarity": "Common" if item["symbol"] in ["FUEL", "FOOD"] else "Rare"
                        } for item in cargo["inventory"]
                    ],
                    "recommendations": [
                        "Cargo arrangement is optimal",
                        "No maintenance required",
                        f"Consider selling {cargo['inventory'][0]['symbol'] if cargo['inventory'] else 'N/A'} at next marketplace"
                    ]
                }
            }
        }
    
    # For real API implementation
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/cargo/scan", 
                                   headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SmugglingRequest(BaseModel):
    action: str  # "hide", "reveal", "configure_compartment"
    cargo_symbol: Optional[str] = None
    compartment_id: Optional[int] = None

@app.post("/api/ships/{ship_symbol}/smuggling")
async def smuggling_operations(ship_symbol: str, request: SmugglingRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Manage smuggling operations and hidden compartments"""
    if not HAS_VALID_TOKEN:
        # Mock smuggling response
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Initialize smuggling data if not exists
        if "smuggling" not in mock_ship:
            mock_ship["smuggling"] = {
                "hidden_compartments": [],
                "max_compartments": 2,
                "stealth_rating": 75,
                "detection_risk": "Low"
            }
        
        smuggling_data = mock_ship["smuggling"]
        
        if request.action == "configure_compartment":
            if len(smuggling_data["hidden_compartments"]) < smuggling_data["max_compartments"]:
                new_compartment = {
                    "id": len(smuggling_data["hidden_compartments"]) + 1,
                    "capacity": 10,
                    "contents": [],
                    "stealth_level": "Standard"
                }
                smuggling_data["hidden_compartments"].append(new_compartment)
                
        elif request.action == "hide" and request.cargo_symbol:
            # Find cargo item and move to hidden compartment
            cargo_item = next((item for item in mock_ship["cargo"]["inventory"] if item["symbol"] == request.cargo_symbol), None)
            if cargo_item and smuggling_data["hidden_compartments"]:
                compartment = smuggling_data["hidden_compartments"][0]
                if len(compartment["contents"]) < compartment["capacity"]:
                    compartment["contents"].append({
                        "symbol": cargo_item["symbol"],
                        "units": min(cargo_item["units"], 5),  # Hide some units
                        "concealment": "Active"
                    })
                    cargo_item["units"] -= min(cargo_item["units"], 5)
                    if cargo_item["units"] <= 0:
                        mock_ship["cargo"]["inventory"].remove(cargo_item)
        
        elif request.action == "reveal":
            # Move items back from hidden compartments
            for compartment in smuggling_data["hidden_compartments"]:
                for hidden_item in compartment["contents"]:
                    existing_item = next((item for item in mock_ship["cargo"]["inventory"] if item["symbol"] == hidden_item["symbol"]), None)
                    if existing_item:
                        existing_item["units"] += hidden_item["units"]
                    else:
                        mock_ship["cargo"]["inventory"].append({
                            "symbol": hidden_item["symbol"],
                            "name": hidden_item["symbol"].replace("_", " ").title(),
                            "description": f"A unit of {hidden_item['symbol']}",
                            "units": hidden_item["units"]
                        })
                compartment["contents"] = []
        
        return {
            "data": {
                "smuggling_status": smuggling_data,
                "message": f"Smuggling operation '{request.action}' completed successfully"
            }
        }
    
    # For real API implementation
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        payload = request.dict()
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/smuggling", 
                                   json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ships/{ship_symbol}/smuggling/status")
async def get_smuggling_status(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get current smuggling status and hidden compartment information"""
    if not HAS_VALID_TOKEN:
        # Mock smuggling status
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        smuggling_data = mock_ship.get("smuggling", {
            "hidden_compartments": [],
            "max_compartments": 2,
            "stealth_rating": 75,
            "detection_risk": "Low"
        })
        
        return {"data": smuggling_data}
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/smuggling/status", 
                                  headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
