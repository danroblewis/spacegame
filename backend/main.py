from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
from routers import (
    agent_router, ships_router, systems_router, factions_router,
    equipment_router, crew_router, security_router, scanning_router,
    resources_router
)

app = FastAPI(title="SpaceTraders GUI Backend", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(agent_router)
app.include_router(ships_router)
app.include_router(systems_router)
app.include_router(factions_router)
app.include_router(equipment_router)
app.include_router(crew_router)
app.include_router(security_router)
app.include_router(scanning_router)
app.include_router(resources_router)

@app.get("/")
async def root():
    return {"message": "SpaceTraders GUI Backend API"}

@app.get("/api/status")
async def get_status():
    """Get SpaceTraders API status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.spacetraders.io/v2")
            return response.json()
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)