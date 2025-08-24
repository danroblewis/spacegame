from .agent import router as agent_router
from .ships import router as ships_router
from .systems import router as systems_router
from .factions import router as factions_router
from .equipment import router as equipment_router
from .crew import router as crew_router
from .security import router as security_router
from .scanning import router as scanning_router
from .resources import router as resources_router

__all__ = [
    "agent_router", "ships_router", "systems_router", "factions_router",
    "equipment_router", "crew_router", "security_router", "scanning_router",
    "resources_router"
]