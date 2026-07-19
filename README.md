# BullionBear Portal

Company application portal. Each card opens an internal tool (Grafana, Jira, GitLab, or any custom URL).

- **Frontend:** Svelte + Vite
- **Backend:** Python FastAPI

## Quick start

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` to the FastAPI server.

## Configure applications

Edit `backend/app/data/apps.json`, or use the API:

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/portal` | Company name and tagline |
| `GET` | `/api/apps` | List enabled apps |
| `POST` | `/api/apps` | Create an app |
| `PUT` | `/api/apps/{id}` | Update an app |
| `DELETE` | `/api/apps/{id}` | Delete an app |

Example app entry:

```json
{
  "id": "grafana",
  "name": "Grafana",
  "description": "Metrics, logs, and operational dashboards",
  "url": "https://grafana.example.com",
  "category": "Observability",
  "color": "#F46800",
  "order": 10,
  "enabled": true
}
```

Card icons are loaded from each app’s favicon; if unavailable, a colored capital letter is shown.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORTAL_COMPANY_NAME` | `BullionBear` | Brand shown in the hero |
| `PORTAL_TAGLINE` | `Company applications at a glance` | Subtitle under the brand |
| `PORTAL_APPS_FILE` | `backend/app/data/apps.json` | Path to apps JSON |
| `PORTAL_CORS_ORIGINS` | `["http://localhost:5173", ...]` | Allowed frontend origins |

## Project layout

```
portal/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes
│   │   ├── models.py        # Pydantic schemas
│   │   ├── store.py         # JSON persistence
│   │   └── data/apps.json   # Application catalog
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.svelte       # Portal page
        └── lib/AppCard.svelte
```
