# Routers package
from .auth import router as auth_router
from .profiles import router as profiles_router
from .matches import router as matches_router

__all__ = ["auth_router", "profiles_router", "matches_router"]
