from fastapi import APIRouter, HTTPException
from models import SecurityActionRequest, SecurityStatus
from services import ship_security_status

router = APIRouter(prefix="/api", tags=["security"])

@router.get("/ships/{ship_symbol}/security/status", response_model=SecurityStatus)
async def get_ship_security_status(ship_symbol: str):
    """Get current security status for a ship"""
    if ship_symbol not in ship_security_status:
        ship_security_status[ship_symbol] = SecurityStatus()
    return ship_security_status[ship_symbol]

@router.post("/ships/{ship_symbol}/security/cloaking")
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

@router.post("/ships/{ship_symbol}/security/jamming")
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

@router.post("/ships/{ship_symbol}/security/countermeasures")
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

@router.post("/ships/{ship_symbol}/security/recharge-countermeasures")
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