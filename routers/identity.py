"""Identity & authentication endpoints."""
from fastapi import APIRouter, Request
from databricks.sdk import WorkspaceClient

router = APIRouter(prefix="/api/v1/identity", tags=["identity"])


@router.get("/me")
async def get_me(request: Request):
    """Return current user info from Databricks Apps HTTP headers."""
    headers = request.headers
    email    = headers.get("x-forwarded-email", "")
    username = headers.get("x-forwarded-preferred-username", "")
    user_id  = headers.get("x-forwarded-user", "")
    ip       = headers.get("x-real-ip", "")
    token    = headers.get("x-forwarded-access-token", "")

    result = {
        "email": email,
        "username": username,
        "user_id": user_id,
        "ip": ip,
        "has_token": bool(token),
        "groups": [],
        "display_name": "",
        "active": None,
        "workspace_id": None,
    }

    if token:
        try:
            w = WorkspaceClient(token=token, auth_type="pat")
            me = w.current_user.me()
            result["display_name"] = me.display_name or ""
            result["active"] = me.active
            result["groups"] = [g.display for g in (me.groups or []) if g.display]
            try:
                result["workspace_id"] = str(w.get_workspace_id())
            except Exception:
                pass
        except Exception as e:
            result["sdk_error"] = str(e)

    return result
