from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .config import settings
from .models import App, AppCreate, AppUpdate, PortalInfo
from .session import get_current_user
from .store import AppStore

store = AppStore(settings.apps_file)

app = FastAPI(
    title=f"{settings.company_name} Portal API",
    description="API for the company application portal",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

public = APIRouter(prefix="/api/public", tags=["public"])
private = APIRouter(
    prefix="/api/private",
    tags=["private"],
    dependencies=[Depends(get_current_user)],
)


@public.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@public.get("/portal", response_model=PortalInfo)
def portal_info() -> PortalInfo:
    return PortalInfo(company=settings.company_name, tagline=settings.tagline)


@public.get("/apps", response_model=list[App])
def list_public_apps() -> list[App]:
    """Enabled apps only — safe for the public portal."""
    return store.list_apps(include_disabled=False)


@private.get("/apps", response_model=list[App])
def list_private_apps() -> list[App]:
    """All apps including disabled — for admin."""
    return store.list_apps(include_disabled=True)


@private.get("/apps/{app_id}", response_model=App)
def get_app(app_id: str) -> App:
    return store.get_app(app_id)


@private.post("/apps", response_model=App, status_code=201)
def create_app(payload: AppCreate) -> App:
    return store.create_app(payload)


@private.put("/apps/{app_id}", response_model=App)
def update_app(app_id: str, payload: AppUpdate) -> App:
    return store.update_app(app_id, payload)


@private.delete("/apps/{app_id}", status_code=204)
def delete_app(app_id: str) -> None:
    store.delete_app(app_id)


public.include_router(auth_router)
app.include_router(public)
app.include_router(private)
