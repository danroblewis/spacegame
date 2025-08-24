from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .routers import core, ships, security, scanning, resources, crew, combat, modifications

app = FastAPI(title="SpaceTraders GUI Backend", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(core.router)
app.include_router(ships.router)
app.include_router(security.router)
app.include_router(scanning.router)
app.include_router(resources.router)
app.include_router(crew.router)
app.include_router(combat.router)
app.include_router(modifications.router)

@app.get("/")
async def root():
    return {"message": "SpaceTraders GUI Backend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)