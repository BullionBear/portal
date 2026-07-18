import json
import threading
from pathlib import Path

from fastapi import HTTPException

from .models import App, AppCreate, AppUpdate


class AppStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def list_apps(self, *, include_disabled: bool = False) -> list[App]:
        apps = self._read()
        if not include_disabled:
            apps = [app for app in apps if app.enabled]
        return sorted(apps, key=lambda app: (app.order, app.name.lower()))

    def get_app(self, app_id: str) -> App:
        for app in self._read():
            if app.id == app_id:
                return app
        raise HTTPException(status_code=404, detail=f"App '{app_id}' not found")

    def create_app(self, payload: AppCreate) -> App:
        with self._lock:
            apps = self._read()
            if any(app.id == payload.id for app in apps):
                raise HTTPException(
                    status_code=409, detail=f"App '{payload.id}' already exists"
                )
            app = App.model_validate(payload.model_dump())
            apps.append(app)
            self._write(apps)
            return app

    def update_app(self, app_id: str, payload: AppUpdate) -> App:
        with self._lock:
            apps = self._read()
            for index, app in enumerate(apps):
                if app.id != app_id:
                    continue
                updated = app.model_copy(
                    update=payload.model_dump(exclude_unset=True)
                )
                apps[index] = updated
                self._write(apps)
                return updated
            raise HTTPException(status_code=404, detail=f"App '{app_id}' not found")

    def delete_app(self, app_id: str) -> None:
        with self._lock:
            apps = self._read()
            next_apps = [app for app in apps if app.id != app_id]
            if len(next_apps) == len(apps):
                raise HTTPException(status_code=404, detail=f"App '{app_id}' not found")
            self._write(next_apps)

    def _read(self) -> list[App]:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [App.model_validate(item) for item in raw]

    def _write(self, apps: list[App]) -> None:
        payload = [app.model_dump(mode="json") for app in apps]
        self.path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
