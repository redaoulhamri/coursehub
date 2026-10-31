# api/__init__.py

from fastapi import FastAPI

from .auth  import auth_router
from .views import views_router
from .admin import admin_router
 

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.include_router(auth_router, prefix="/v1")
app.include_router(views_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")


