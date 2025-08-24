from pydantic import BaseModel
from typing import Optional, List

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

class SurveyRequest(BaseModel):
    shipSymbol: str

# Additional crew request that was duplicated in main.py
class HireCrewRequest(BaseModel):
    hireableCrewId: str