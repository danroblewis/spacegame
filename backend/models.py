from pydantic import BaseModel
from typing import List, Optional, Union

# Basic models
class Agent(BaseModel):
    symbol: str
    headquarters: str
    credits: int
    startingFaction: str

# Ship modification models
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

# Crew management models
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

# Ship and system models
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

# Action request models
class NavigateRequest(BaseModel):
    waypointSymbol: str

class CombatActionRequest(BaseModel):
    action: str
    target: Optional[str] = None
    params: Optional[dict] = None

class RefuelRequest(BaseModel):
    units: Optional[int] = None

class TransferRequest(BaseModel):
    tradeSymbol: str
    units: int
    shipSymbol: str

class RepairRequest(BaseModel):
    pass  # No specific parameters needed for repair

class ScrapRequest(BaseModel):
    pass  # No specific parameters needed for scrap

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

# Scanning & Intelligence Models
class ScanResult(BaseModel):
    shipSymbol: str
    scanType: str
    timestamp: str
    data: dict
    cooldown: Optional[dict] = None

class SurveyRequest(BaseModel):
    shipSymbol: str

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