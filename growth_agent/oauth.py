from __future__ import annotations

from urllib.parse import urlencode


GOOGLE_ADS_SCOPE = "https://www.googleapis.com/auth/adwords"
GOOGLE_AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
META_GRAPH_BASE_URL = "https://graph.facebook.com"


def build_google_ads_authorization_url(
    client_id: str,
    redirect_uri: str,
    state: str,
) -> str:
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_ADS_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    return f"{GOOGLE_AUTH_BASE_URL}?{query}"


def build_google_ads_token_payload(
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
) -> tuple[str, dict[str, str]]:
    return GOOGLE_TOKEN_URL, {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }


def build_meta_debug_token_url(
    app_id: str,
    app_secret: str,
    input_token: str,
) -> str:
    query = urlencode(
        {
            "input_token": input_token,
            "access_token": f"{app_id}|{app_secret}",
        }
    )
    return f"{META_GRAPH_BASE_URL}/debug_token?{query}"
