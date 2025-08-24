from pydantic import BaseModel
from typing import Optional

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