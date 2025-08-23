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
