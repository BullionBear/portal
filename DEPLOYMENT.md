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

| Path | Service | Auth |
|------|---------|------|
| `portal.lynkora.com/api/public/*` | `backend:8000` | none (includes Discord login/callback) |
| `portal.lynkora.com/api/private/*` | `backend:8000` | Discord session cookie |
| `portal.lynkora.com/*` | `frontend:80` — nginx SPA | none |

Same-origin, so the browser makes no cross-origin calls and no CORS config is needed.

### Discord OAuth (one-time on the server)

Admin auth is **native Discord OAuth2 in the FastAPI backend** (oauth2-proxy has no
Discord provider). Guild membership is checked with the `guilds` scope.

1. Discord Developer Portal → OAuth2 → Redirects, add:  
   `https://portal.lynkora.com/api/public/auth/discord/callback`
2. On the host, create `/opt/portal/deploy/.env` from [`deploy/.env.example`](deploy/.env.example):

```bash
ssh root@139.162.74.23
cd /opt/portal/deploy
# fill DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, SESSION_SECRET
openssl rand -base64 32   # -> SESSION_SECRET
docker compose -p portal up -d
```

CI syncs only `docker-compose.yml`; **`.env` is not overwritten** by deploys.

## CI/CD (`.github/workflows/deploy.yml`)

On every push to `main`:

1. **build** (matrix: backend, frontend) — build each image, push `:latest` and
   `:<sha>` to GHCR. Auth via the workflow's `GITHUB_TOKEN` (`packages: write`).
2. **deploy** — SSH to the host, `scp` the compose file to `/opt/portal/deploy/`,
   then `docker compose -p portal pull && up -d && docker image prune -f`.
3. **notify** — Discord webhook with commit hash and message.

### Repo secrets (already set)

| Secret | Value |
|--------|-------|
| `SSH_PRIVATE_KEY` | dedicated ed25519 deploy key (public half in the server's `authorized_keys`) |
| `SERVER_HOST` | `139.162.74.23` |
| `SERVER_USER` | `root` |
| `DISCORD_WEBHOOK_URL` | Discord incoming webhook URL for deploy result notifications |

The deploy job logs the server into GHCR with the workflow `GITHUB_TOKEN`
(`packages: read`) before `docker compose pull`, so no long-lived registry
credential is required on the host.

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
curl -I https://portal.lynkora.com/                   # 200
curl https://portal.lynkora.com/api/public/health     # {"status":"ok"}
curl https://portal.lynkora.com/api/public/apps       # enabled app catalog JSON
curl -I https://portal.lynkora.com/api/private/apps   # 401 without session
curl -I 'https://portal.lynkora.com/api/public/auth/discord/login?rd=/admin'  # 302 → Discord
```

## Data persistence

The apps catalog (`backend/app/data/apps.json`) is mounted on the named volume
`portal-data`, so edits made through the API survive image updates and redeploys.
