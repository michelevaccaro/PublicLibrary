"""Login Microsoft (OAuth) per accedere a OneDrive via Microsoft Graph.

Richiede tre variabili d'ambiente (impostate su Render, mai nel codice):
    ONEDRIVE_CLIENT_ID
    ONEDRIVE_CLIENT_SECRET
    ONEDRIVE_TENANT_ID  (o "common" se l'app registrata accetta anche
                          account Microsoft personali, non solo organizzativi)

Il token (incluso il refresh token) viene salvato in un file locale sul
server: va bene per un'app a singolo utente come questa. Su Render free
tier il disco è effimero, quindi dopo un redeploy potrebbe servire un
nuovo login.
"""

import os

import msal

SCOPES = ["Files.ReadWrite"]  # offline_access è aggiunto automaticamente da MSAL per le confidential client app
TOKEN_CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", ".token_cache.bin")


def _load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_PATH):
        with open(TOKEN_CACHE_PATH, "r") as f:
            cache.deserialize(f.read())
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        with open(TOKEN_CACHE_PATH, "w") as f:
            f.write(cache.serialize())


class NotConfiguredError(RuntimeError):
    pass


def is_configured():
    return bool(os.environ.get("ONEDRIVE_CLIENT_ID")) and bool(os.environ.get("ONEDRIVE_CLIENT_SECRET"))


def _authority():
    tenant_id = os.environ.get("ONEDRIVE_TENANT_ID", "common")
    return f"https://login.microsoftonline.com/{tenant_id}"


def _build_app(cache=None):
    if not is_configured():
        raise NotConfiguredError(
            "OneDrive non configurato sul server: mancano le variabili d'ambiente "
            "ONEDRIVE_CLIENT_ID / ONEDRIVE_CLIENT_SECRET."
        )
    return msal.ConfidentialClientApplication(
        client_id=os.environ["ONEDRIVE_CLIENT_ID"],
        client_credential=os.environ["ONEDRIVE_CLIENT_SECRET"],
        authority=_authority(),
        token_cache=cache,
    )


def get_auth_url(redirect_uri, state):
    app = _build_app()
    return app.get_authorization_request_url(SCOPES, redirect_uri=redirect_uri, state=state)


def acquire_token_by_auth_code(code, redirect_uri):
    cache = _load_cache()
    app = _build_app(cache)
    result = app.acquire_token_by_authorization_code(code, scopes=SCOPES, redirect_uri=redirect_uri)
    _save_cache(cache)
    if "access_token" not in result:
        raise RuntimeError(f"Login fallito: {result.get('error_description', result)}")
    return result


def get_access_token():
    """Ritorna un access token valido (silenziosamente rinnovato se serve),
    o None se non c'è nessun login salvato (o se OneDrive non è configurato)."""
    if not is_configured():
        return None
    cache = _load_cache()
    app = _build_app(cache)
    accounts = app.get_accounts()
    if not accounts:
        return None
    result = app.acquire_token_silent(SCOPES, account=accounts[0])
    _save_cache(cache)
    if result is None or "access_token" not in result:
        return None
    return result["access_token"]


def is_logged_in():
    return get_access_token() is not None


def logout():
    if os.path.exists(TOKEN_CACHE_PATH):
        os.remove(TOKEN_CACHE_PATH)
