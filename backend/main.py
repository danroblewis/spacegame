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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
