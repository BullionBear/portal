from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import App, AppCreate, AppUpdate, PortalInfo
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


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/portal", response_model=PortalInfo)
def portal_info() -> PortalInfo:
    return PortalInfo(company=settings.company_name, tagline=settings.tagline)


@app.get("/api/apps", response_model=list[App])
def list_apps(
    include_disabled: bool = Query(default=False),
) -> list[App]:
    return store.list_apps(include_disabled=include_disabled)


@app.get("/api/apps/{app_id}", response_model=App)
def get_app(app_id: str) -> App:
    return store.get_app(app_id)


@app.post("/api/apps", response_model=App, status_code=201)
def create_app(payload: AppCreate) -> App:
    return store.create_app(payload)


@app.put("/api/apps/{app_id}", response_model=App)
def update_app(app_id: str, payload: AppUpdate) -> App:
    return store.update_app(app_id, payload)


@app.delete("/api/apps/{app_id}", status_code=204)
def delete_app(app_id: str) -> None:
    store.delete_app(app_id)
