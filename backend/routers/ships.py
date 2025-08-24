from fastapi import APIRouter, HTTPException, Depends
from typing import List
import httpx

from ..models import Ship, NavigateRequest, RefuelRequest, TransferRequest, ModificationRequest, CustomizationRequest
from ..config import HAS_VALID_TOKEN, SPACETRADERS_API_URL, SPACETRADERS_TOKEN, SHIP_COLORS, SHIP_DECALS
from ..mock_data import MOCK_SHIPS, MOCK_AGENT, MOCK_WAYPOINTS, MOCK_EQUIPMENT
from ..utilities import get_httpx_client

router = APIRouter(prefix="/api/ships", tags=["ships"])

@router.get("", response_model=List[Ship])
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

@router.post("/{ship_symbol}/navigate")
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

@router.post("/{ship_symbol}/dock")
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

@router.post("/{ship_symbol}/orbit")
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

@router.post("/{ship_symbol}/refuel")
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

@router.get("/{ship_symbol}/repair")
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

@router.post("/{ship_symbol}/repair")
async def repair_ship(ship_symbol: str, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Repair ship at current waypoint"""
    if not HAS_VALID_TOKEN:
        # Mock repair response
        return {
            "data": {
                "agent": {"credits": 999900},
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
        response = await client.post(f"{SPACETRADERS_API_URL}/my/ships/{ship_symbol}/repair", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{ship_symbol}/transfer")
async def transfer_cargo(ship_symbol: str, request: TransferRequest, client: httpx.AsyncClient = Depends(get_httpx_client)):
    """Transfer cargo between ships"""
    if not HAS_VALID_TOKEN:
        # Mock transfer response
        source_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == ship_symbol), None)
        target_ship = next((ship for ship in MOCK_SHIPS if ship["symbol"] == request.shipSymbol), None)
        
        if not source_ship or not target_ship:
            raise HTTPException(status_code=404, detail="Ship not found")
        
        # Mock cargo transfer logic
        source_item = next((item for item in source_ship["cargo"]["inventory"] if item["symbol"] == request.tradeSymbol), None)
        if not source_item or source_item["units"] < request.units:
            raise HTTPException(status_code=400, detail="Insufficient cargo")
        
        # Update mock cargo
        source_item["units"] -= request.units
        if source_item["units"] == 0:
            source_ship["cargo"]["inventory"].remove(source_item)
        
        target_item = next((item for item in target_ship["cargo"]["inventory"] if item["symbol"] == request.tradeSymbol), None)
        if target_item:
            target_item["units"] += request.units
        else:
            target_ship["cargo"]["inventory"].append({"symbol": request.tradeSymbol, "units": request.units})
        
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