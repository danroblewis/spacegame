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

class CrewMember(BaseModel):
    id: str
    name: str
    role: str  # PILOT, ENGINEER, GUNNER, MEDIC, SECURITY, MINER, etc.
    level: int
    experience: int
    skills: dict  # {"piloting": 75, "engineering": 60, "combat": 45}
    health: int  # 0-100
    morale: int  # 0-100
    salary: int  # Credits per day
    hired_date: str
    status: str  # ACTIVE, INJURED, RESTING, TRAINING

class CrewQuarters(BaseModel):
    capacity: int
    comfort_level: int  # 1-5, affects morale
    facilities: List[str]  # ["recreation_room", "private_cabins", "gym"]
    maintenance_cost: int  # Credits per day

class MedicalBay(BaseModel):
    level: int  # 1-5, affects treatment effectiveness
    capacity: int  # Number of patients that can be treated simultaneously
    equipment: List[str]  # ["basic_med_kit", "surgery_suite", "bio_scanner"]
    treatment_cost: int  # Credits per treatment

class CrewTrainingFacility(BaseModel):
    level: int  # 1-5, affects training effectiveness
    programs: List[str]  # ["pilot_training", "engineering_course", "combat_drill"]
    training_cost: int  # Credits per training session

class HireCrewRequest(BaseModel):
    role: str
    max_salary: int

class TrainCrewRequest(BaseModel):
    skill: str
    duration_hours: int

class AssignRoleRequest(BaseModel):
    new_role: str

class TreatCrewRequest(BaseModel):
    crew_ids: List[str]

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
    units: Optional[int] = None  # If not specified, refuel to max capacity

class TransferCargoRequest(BaseModel):
    tradeSymbol: str
    units: int
    shipSymbol: str  # Target ship to transfer to

# Mock data for testing
MOCK_AGENT = {
    "symbol": "DEMO_AGENT",
    "headquarters": "X1-DF55-20250X",
    "credits": 1000000,
    "startingFaction": "COSMIC"
}

MOCK_CREW_MEMBERS = {
    "DEMO_SHIP_1": [
        {
            "id": "crew_001",
            "name": "Captain Sarah Chen",
            "role": "PILOT",
            "level": 5,
            "experience": 2500,
            "skills": {"piloting": 85, "leadership": 90, "navigation": 80},
            "health": 95,
            "morale": 85,
            "salary": 150,
            "hired_date": "2023-10-01T00:00:00.000Z",
            "status": "ACTIVE"
        },
        {
            "id": "crew_002",
            "name": "Engineer Marcus Rodriguez",
            "role": "ENGINEER",
            "level": 4,
            "experience": 1800,
            "skills": {"engineering": 88, "repair": 85, "systems": 75},
            "health": 100,
            "morale": 90,
            "salary": 120,
            "hired_date": "2023-10-01T00:00:00.000Z",
            "status": "ACTIVE"
        }
    ]
}

MOCK_CREW_QUARTERS = {
    "DEMO_SHIP_1": {
        "capacity": 4,
        "comfort_level": 3,
        "facilities": ["recreation_room", "private_cabins"],
        "maintenance_cost": 50
    }
}

MOCK_MEDICAL_BAY = {
    "DEMO_SHIP_1": {
        "level": 2,
        "capacity": 2,
        "equipment": ["basic_med_kit", "bio_scanner"],
        "treatment_cost": 100
    }
}

MOCK_TRAINING_FACILITY = {
    "DEMO_SHIP_1": {
        "level": 2,
        "programs": ["pilot_training", "engineering_course"],
        "training_cost": 200
    }
}

MOCK_AVAILABLE_CREW = [
    {
        "id": "hire_001",
        "name": "Alex Thompson",
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

# In-memory storage for automation configs (in production, use a database)
automation_configs = {
    "auto_trade": {},
    "combat_ai": {},
    "crew_rotation": {},
    "maintenance": [],
    "resource_monitoring": {}
}

# API endpoints
@app.get("/")
async def root():
    return {"message": "SpaceTraders GUI Backend API"}

# Crew Management Endpoints
@app.get("/api/ships/{ship_symbol}/crew", response_model=List[CrewMember])
async def get_ship_crew(ship_symbol: str):
    """Get crew roster for a specific ship"""
    if not HAS_VALID_TOKEN:
        return MOCK_CREW_MEMBERS.get(ship_symbol, [])
    
    # TODO: Implement real SpaceTraders API call when available
    return MOCK_CREW_MEMBERS.get(ship_symbol, [])

@app.get("/api/ships/{ship_symbol}/crew/available")
async def get_available_crew(ship_symbol: str):
    """Get available crew members for hire"""
    if not HAS_VALID_TOKEN:
        return MOCK_AVAILABLE_CREW
    
    # TODO: Implement real SpaceTraders API call when available
    return MOCK_AVAILABLE_CREW

@app.post("/api/ships/{ship_symbol}/crew/hire")
async def hire_crew(ship_symbol: str, request: HireCrewRequest):
    """Hire a new crew member"""
    if not HAS_VALID_TOKEN:
        # Find available crew member matching the role
        available_crew = [crew for crew in MOCK_AVAILABLE_CREW 
                         if crew["role"] == request.role and crew["salary"] <= request.max_salary]
        
        if not available_crew:
            raise HTTPException(status_code=404, detail="No suitable crew member found")
        
        # Select the first suitable crew member
        hired_crew = available_crew[0].copy()
        hired_crew["id"] = f"crew_{len(MOCK_CREW_MEMBERS.get(ship_symbol, [])) + 1:03d}"
        hired_crew["experience"] = 0
        hired_crew["health"] = 100
        hired_crew["morale"] = 80
        hired_crew["hired_date"] = "2023-11-01T00:00:00.000Z"
        hired_crew["status"] = "ACTIVE"
        
        # Add to ship's crew
        if ship_symbol not in MOCK_CREW_MEMBERS:
            MOCK_CREW_MEMBERS[ship_symbol] = []
        MOCK_CREW_MEMBERS[ship_symbol].append(hired_crew)
        
        # Update ship crew count
        for ship in MOCK_SHIPS:
            if ship["symbol"] == ship_symbol:
                ship["crew"]["current"] += 1
                break
        
        return {"data": hired_crew, "message": f"Successfully hired {hired_crew['name']}"}
    
    # TODO: Implement real SpaceTraders API call when available
    raise HTTPException(status_code=501, detail="Not implemented for real API yet")

@app.delete("/api/ships/{ship_symbol}/crew/{crew_id}")
async def fire_crew(ship_symbol: str, crew_id: str):
    """Fire a crew member"""
    if not HAS_VALID_TOKEN:
        ship_crew = MOCK_CREW_MEMBERS.get(ship_symbol, [])
        crew_member = next((crew for crew in ship_crew if crew["id"] == crew_id), None)
        
        if not crew_member:
            raise HTTPException(status_code=404, detail="Crew member not found")
        
        # Remove from ship's crew
        MOCK_CREW_MEMBERS[ship_symbol] = [crew for crew in ship_crew if crew["id"] != crew_id]
        
        # Update ship crew count
        for ship in MOCK_SHIPS:
            if ship["symbol"] == ship_symbol:
                ship["crew"]["current"] -= 1
                break
        
        return {"data": crew_member, "message": f"Successfully fired {crew_member['name']}"}
    
    # TODO: Implement real SpaceTraders API call when available
    raise HTTPException(status_code=501, detail="Not implemented for real API yet")

@app.put("/api/ships/{ship_symbol}/crew/{crew_id}/train")
async def train_crew(ship_symbol: str, crew_id: str, request: TrainCrewRequest):
    """Train a crew member to improve their skills"""
    if not HAS_VALID_TOKEN:
        ship_crew = MOCK_CREW_MEMBERS.get(ship_symbol, [])
        crew_member = next((crew for crew in ship_crew if crew["id"] == crew_id), None)
        
        if not crew_member:
            raise HTTPException(status_code=404, detail="Crew member not found")
        
        if crew_member["status"] != "ACTIVE":
            raise HTTPException(status_code=400, detail="Crew member is not available for training")
        
        # Improve skill based on training
        skill_improvement = min(10, request.duration_hours // 2)  # 5 points per hour
        current_skill = crew_member["skills"].get(request.skill, 0)
        new_skill_level = min(100, current_skill + skill_improvement)
        
        crew_member["skills"][request.skill] = new_skill_level
        crew_member["experience"] += request.duration_hours * 10
        crew_member["status"] = "TRAINING"
        
        # Calculate new level based on experience
        new_level = min(10, crew_member["experience"] // 500 + 1)
        crew_member["level"] = new_level
        
        return {
            "data": crew_member,
            "message": f"Training completed. {request.skill} improved to {new_skill_level}"
        }
    
    # TODO: Implement real SpaceTraders API call when available
    raise HTTPException(status_code=501, detail="Not implemented for real API yet")

@app.put("/api/ships/{ship_symbol}/crew/{crew_id}/assign")
async def assign_crew_role(ship_symbol: str, crew_id: str, request: AssignRoleRequest):
    """Assign a new role to a crew member"""
    if not HAS_VALID_TOKEN:
        ship_crew = MOCK_CREW_MEMBERS.get(ship_symbol, [])
        crew_member = next((crew for crew in ship_crew if crew["id"] == crew_id), None)
        
        if not crew_member:
            raise HTTPException(status_code=404, detail="Crew member not found")
        
        old_role = crew_member["role"]
        crew_member["role"] = request.new_role
        
        return {
            "data": crew_member,
            "message": f"Successfully reassigned {crew_member['name']} from {old_role} to {request.new_role}"
        }
    
    # TODO: Implement real SpaceTraders API call when available
    raise HTTPException(status_code=501, detail="Not implemented for real API yet")

@app.get("/api/ships/{ship_symbol}/crew/quarters", response_model=CrewQuarters)
async def get_crew_quarters(ship_symbol: str):
    """Get crew quarters information"""
    if not HAS_VALID_TOKEN:
        quarters = MOCK_CREW_QUARTERS.get(ship_symbol)
        if not quarters:
            raise HTTPException(status_code=404, detail="Ship not found")
        return quarters
    
    # TODO: Implement real SpaceTraders API call when available
    return MOCK_CREW_QUARTERS.get(ship_symbol, {})

@app.put("/api/ships/{ship_symbol}/crew/quarters")
async def upgrade_crew_quarters(ship_symbol: str):
    """Upgrade crew quarters to improve comfort and morale"""
    if not HAS_VALID_TOKEN:
        quarters = MOCK_CREW_QUARTERS.get(ship_symbol)
        if not quarters:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        if quarters["comfort_level"] >= 5:
            raise HTTPException(status_code=400, detail="Quarters already at maximum level")
        
        # Upgrade quarters
        quarters["comfort_level"] += 1
        quarters["maintenance_cost"] += 25
        
        # Add new facilities
        new_facilities = {
            2: "private_cabins",
            3: "recreation_room", 
            4: "gym",
            5: "luxury_suites"
        }
        
        new_facility = new_facilities.get(quarters["comfort_level"])
        if new_facility and new_facility not in quarters["facilities"]:
            quarters["facilities"].append(new_facility)
        
        # Improve crew morale
        ship_crew = MOCK_CREW_MEMBERS.get(ship_symbol, [])
        for crew_member in ship_crew:
            crew_member["morale"] = min(100, crew_member["morale"] + 10)
        
        return {
            "data": quarters,
            "message": f"Quarters upgraded to level {quarters['comfort_level']}"
        }
    
    # TODO: Implement real SpaceTraders API call when available
    raise HTTPException(status_code=501, detail="Not implemented for real API yet")

@app.get("/api/ships/{ship_symbol}/crew/medical", response_model=MedicalBay)
async def get_medical_bay(ship_symbol: str):
    """Get medical bay information"""
    if not HAS_VALID_TOKEN:
        medical_bay = MOCK_MEDICAL_BAY.get(ship_symbol)
        if not medical_bay:
            raise HTTPException(status_code=404, detail="Ship not found")
        return medical_bay
    
    # TODO: Implement real SpaceTraders API call when available
    return MOCK_MEDICAL_BAY.get(ship_symbol, {})

@app.post("/api/ships/{ship_symbol}/crew/medical/treat")
async def treat_injured_crew(ship_symbol: str, request: TreatCrewRequest):
    """Treat injured crew members in the medical bay"""
    if not HAS_VALID_TOKEN:
        ship_crew = MOCK_CREW_MEMBERS.get(ship_symbol, [])
        medical_bay = MOCK_MEDICAL_BAY.get(ship_symbol)
        
        if not medical_bay:
            raise HTTPException(status_code=404, detail="Medical bay not found")
        
        treated_crew = []
        for crew_id in request.crew_ids:
            crew_member = next((crew for crew in ship_crew if crew["id"] == crew_id), None)
            if crew_member and crew_member["health"] < 100:
                # Heal the crew member
                health_improvement = min(50, 100 - crew_member["health"])
                crew_member["health"] += health_improvement
                crew_member["status"] = "ACTIVE" if crew_member["health"] >= 90 else "RESTING"
                treated_crew.append(crew_member)
        
        if not treated_crew:
            raise HTTPException(status_code=400, detail="No crew members need treatment")
        
        total_cost = len(treated_crew) * medical_bay["treatment_cost"]
        
        return {
            "data": treated_crew,
            "cost": total_cost,
            "message": f"Successfully treated {len(treated_crew)} crew members"
        }
    
    # TODO: Implement real SpaceTraders API call when available
    raise HTTPException(status_code=501, detail="Not implemented for real API yet")

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
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        if mock_ship["nav"]["status"] != "DOCKED":
            raise HTTPException(status_code=400, detail="Ship must be docked at a shipyard to repair")
        
        return {
            "data": {
                "agent": {"credits": 999900},
                "ship": mock_ship,
                "transaction": {
                    "waypointSymbol": mock_ship["nav"]["waypointSymbol"],
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

@app.get("/api/ships/{ship_symbol}/scrap")
async def get_scrap_value(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Get scrap value for ship"""
    if not HAS_VALID_TOKEN:
        # Mock scrap value response
        return {
            "data": {
                "transaction": {
                    "waypointSymbol": "X1-DF55-20250X",
                    "shipSymbol": ship_symbol,
                    "totalPrice": 50000,
                    "timestamp": "2023-11-01T00:00:00.000Z"
                }
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.get(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/scrap", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ships/{ship_symbol}/scrap")
async def scrap_ship(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Scrap ship at current waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock scrap response - remove ship from mock list
        mock_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        if not mock_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        if mock_ship["nav"]["status"] != "DOCKED":
            raise HTTPException(status_code=400, detail="Ship must be docked at a shipyard to scrap")
        
        # Remove ship from mock list
        MOCK_SHIPS[:] = [ship for ship in MOCK_SHIPS if ship["symbol"] != ship_symbol]
        
        return {
            "data": {
                "agent": {"credits": 1050000},
                "transaction": {
                    "waypointSymbol": mock_ship["nav"]["waypointSymbol"],
                    "shipSymbol": ship_symbol,
                    "totalPrice": 50000,
                    "timestamp": "2023-11-01T00:00:00.000Z"
                }
            }
        }
    
    try:
        headers = {"Authorization": f"Bearer {SPACETRADERS_TOKEN}"}
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/scrap", headers=headers)
        
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
        target_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == request.shipSymbol), None)
        
        if not source_ship:
            raise HTTPException(status_code=404, detail="Source ship not found")
        if not target_ship:
            raise HTTPException(status_code=404, detail="Target ship not found")
        
        # Mock cargo transfer logic
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
