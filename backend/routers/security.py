from fastapi import APIRouter, HTTPException
from ..models import SecurityActionRequest, SecurityStatus
from ..utilities import ship_security_status

router = APIRouter(prefix="/api/ships", tags=["security"])

@router.get("/{ship_symbol}/security/status", response_model=SecurityStatus)
async def get_ship_security_status(ship_symbol: str):
    """Get current security status for a ship"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    return ship_security_status[ship_symbol]

@router.post("/{ship_symbol}/security/cloaking")
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

@router.post("/{ship_symbol}/security/jamming")
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

@router.post("/{ship_symbol}/security/electronic-warfare")
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

@router.post("/{ship_symbol}/security/stealth-mode")
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

@router.post("/{ship_symbol}/security/countermeasures")
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

@router.post("/{ship_symbol}/security/encryption")
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

@router.post("/{ship_symbol}/security/recharge-countermeasures")
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