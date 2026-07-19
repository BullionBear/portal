import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

from .config import settings
from .session import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE,
    STATE_COOKIE_NAME,
    cookie_kwargs,
    create_session_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])

DISCORD_API = "https://discord.com/api/v10"


def _safe_return_path(rd: str | None) -> str:
    if not rd or not rd.startswith("/") or rd.startswith("//"):
        return "/admin"
    return rd


@router.get("/discord/login")
async def discord_login(rd: str | None = None):
    if not settings.discord_client_id or not settings.discord_client_secret:
        return JSONResponse(
            {"detail": "Discord OAuth is not configured"},
            status_code=503,
        )

    state = secrets.token_urlsafe(24)
    return_path = _safe_return_path(rd)
    # Encode return path in state cookie payload via separate cookie value:
    # state|<return_path>
    state_value = f"{state}|{return_path}"

    params = {
        "client_id": settings.discord_client_id,
        "redirect_uri": settings.discord_redirect_uri,
        "response_type": "code",
        "scope": "identify guilds",
        "state": state,
        "prompt": "consent",
    }
    authorize_url = f"{DISCORD_API}/oauth2/authorize?{urlencode(params)}"
    response = RedirectResponse(authorize_url, status_code=302)
    response.set_cookie(
        STATE_COOKIE_NAME,
        state_value,
        max_age=600,
        **cookie_kwargs(),
    )
    return response


@router.get("/discord/callback")
async def discord_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    return_path = "/admin"
    raw_state = request.cookies.get(STATE_COOKIE_NAME, "")
    if "|" in raw_state:
        expected_state, return_path = raw_state.split("|", 1)
        return_path = _safe_return_path(return_path)
    else:
        expected_state = raw_state

    def fail(reason: str) -> RedirectResponse:
        response = RedirectResponse(f"/admin?error={reason}", status_code=302)
        response.delete_cookie(STATE_COOKIE_NAME, **cookie_kwargs())
        return response

    if error:
        return fail("access_denied")
    if not code or not state or not expected_state or state != expected_state:
        return fail("invalid_state")

    async with httpx.AsyncClient(timeout=20.0) as client:
        token_resp = await client.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": settings.discord_client_id,
                "client_secret": settings.discord_client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.discord_redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status_code != 200:
            return fail("token_exchange_failed")
        access_token = token_resp.json()["access_token"]

        user_resp = await client.get(
            f"{DISCORD_API}/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            return fail("user_fetch_failed")
        discord_user = user_resp.json()

        if settings.discord_guild_id:
            guilds_resp = await client.get(
                f"{DISCORD_API}/users/@me/guilds",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if guilds_resp.status_code != 200:
                return fail("guild_check_failed")
            guild_ids = {g.get("id") for g in guilds_resp.json()}
            if settings.discord_guild_id not in guild_ids:
                return fail("not_member")

    session_user = {
        "id": discord_user["id"],
        "username": discord_user.get("username"),
        "global_name": discord_user.get("global_name"),
        "avatar": discord_user.get("avatar"),
    }
    token = create_session_token(session_user)

    response = RedirectResponse(return_path, status_code=302)
    response.delete_cookie(STATE_COOKIE_NAME, **cookie_kwargs())
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=SESSION_MAX_AGE,
        **cookie_kwargs(),
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie(SESSION_COOKIE_NAME, **cookie_kwargs())
    return response


@router.get("/me")
async def me(request: Request):
    return get_current_user(request)
