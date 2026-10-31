# api/admin/__init__.py

from fastapi import APIRouter

# Import the sub-routers from their respective files
from .admins import admins_router
from .catalog import catalog_router
from .documents import documents_router
from .professors import professors_router

# Create the main admin router
admin_router = APIRouter()

# Include all the sub-routers
admin_router.include_router(admins_router)
admin_router.include_router(catalog_router)
admin_router.include_router(documents_router)
admin_router.include_router(professors_router)

