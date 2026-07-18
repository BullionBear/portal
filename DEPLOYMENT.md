# Deployment

## Stack

- **Frontend**: Svelte + Vite, built to static and served by nginx → `portal.lynkora.com`
- **Backend**: FastAPI (uvicorn) → `portal.lynkora.com/api`
- **Reverse proxy / TLS**: the shared standalone **Traefik** on the host
  (compose project `traefik`, `/opt/traefik`; Let's Encrypt, HTTP-01 challenge).
  Apps attach to its external **`web`** network and advertise routes via
  `traefik.*` labels. The portal does **not** run its own Traefik.
- **Host**: `root@139.162.74.23` (shared box; also runs the `autom`, `lynxlinkage-db`
  and `statarb-nats` stacks — the portal is isolated in its own compose project).
- **Registry**: GHCR, private —
  `ghcr.io/bullionbear/portal-backend`, `ghcr.io/bullionbear/portal-frontend`.

## Routing (single host, path-based)

| Path | Service |
|------|---------|
| `portal.lynkora.com/api/*` | `backend:8000` (Traefik router priority 100) |
| `portal.lynkora.com/*` | `frontend:80` — nginx SPA (priority 1) |

Same-origin, so the browser makes no cross-origin calls and no CORS config is needed.

## CI/CD (`.github/workflows/deploy.yml`)

On every push to `main`:

1. **build** (matrix: backend, frontend) — build each image, push `:latest` and
   `:<sha>` to GHCR. Auth via the workflow's `GITHUB_TOKEN` (`packages: write`).
2. **deploy** — SSH to the host, `scp` the compose file to `/opt/portal/deploy/`,
   then `docker compose -p portal pull && up -d && docker image prune -f`.

### Repo secrets (already set)

| Secret | Value |
|--------|-------|
| `SSH_PRIVATE_KEY` | dedicated ed25519 deploy key (public half in the server's `authorized_keys`) |
| `SERVER_HOST` | `139.162.74.23` |
| `SERVER_USER` | `root` |

The server pulls private GHCR images using its existing `ghcr.io` docker login
(account `yitech`, an owner of the `BullionBear` org).

## One-time setup (done)

### DNS (Hostinger)

`portal` A record on `lynkora.com` → `139.162.74.23`, added via the Hostinger DNS
API (`PUT https://developers.hostinger.com/api/dns/v1/zones/lynkora.com` with
`overwrite: false` to merge, not replace, the zone).

### TLS

Traefik requests a cert for `portal.lynkora.com` automatically on first request via
the `le` (Let's Encrypt) resolver. Port 80 must stay reachable from the internet for
the HTTP-01 challenge (already open — the `autom` stack uses the same path).

## Manual deploy (fallback)

```bash
ssh root@139.162.74.23 'cd /opt/portal/deploy && docker compose -p portal pull && docker compose -p portal up -d'
```

## Verify

```bash
curl -I https://portal.lynkora.com/            # 200
curl https://portal.lynkora.com/api/health     # {"status":"ok"}
curl https://portal.lynkora.com/api/apps       # app catalog JSON
```

## Data persistence

The apps catalog (`backend/app/data/apps.json`) is mounted on the named volume
`portal-data`, so edits made through the API survive image updates and redeploys.
