"""Daily heartbeat that keeps a free Supabase project from being paused.

Supabase pauses free projects without "sufficient user database activity over the past week"
(docs/04-arquitectura/arquitectura.md). We make three real requests through the REST API
(PostgREST), which counts as user activity; a plain `SELECT 1` over a direct connection may not.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx

RETENTION_DAYS = 30


@dataclass(frozen=True)
class HeartbeatResult:
    env: str
    markets_read: int
    old_deleted: int


class HeartbeatError(RuntimeError):
    pass


def run_heartbeat(
    base_url: str,
    service_role_key: str,
    env: str,
    *,
    client: httpx.Client | None = None,
    now: datetime | None = None,
) -> HeartbeatResult:
    """Read `markets`, insert a row in `heartbeats`, delete heartbeats older than 30 days."""
    now = now or datetime.now(UTC)
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
    }
    rest = f"{base_url.rstrip('/')}/rest/v1"
    owns_client = client is None
    client = client or httpx.Client(timeout=20)
    try:
        read = client.get(f"{rest}/markets", params={"select": "id", "limit": "1"}, headers=headers)
        _check(read, "leer markets")

        insert = client.post(
            f"{rest}/heartbeats",
            json={"project": env},
            headers={**headers, "Prefer": "return=minimal"},
        )
        _check(insert, "insertar heartbeat")

        cutoff = (now - timedelta(days=RETENTION_DAYS)).isoformat()
        delete = client.delete(
            f"{rest}/heartbeats",
            params={"created_at": f"lt.{cutoff}", "select": "id"},
            headers={**headers, "Prefer": "return=representation"},
        )
        _check(delete, "borrar heartbeats viejos")
    except httpx.HTTPError as exc:  # network errors, timeouts
        raise HeartbeatError(f"error de red: {type(exc).__name__}") from None
    finally:
        if owns_client:
            client.close()

    return HeartbeatResult(env=env, markets_read=len(read.json()), old_deleted=len(delete.json()))


def diagnose_supabase_url(url: str) -> str | None:
    """Explain, without echoing the value, why a URL is not a Supabase API URL (None if fine)."""
    lowered = url.lower()
    if lowered.startswith(("https://postgres", "https://postgresql")) or "@" in lowered:
        return "parece una cadena de conexión Postgres (esa va en SUPABASE_DB_URL_*)"
    host = httpx.URL(url).host
    if host.endswith("supabase.com"):
        return "parece la URL del panel de Supabase; usa la 'Project URL' de Settings > API"
    if not host.endswith(".supabase.co"):
        return "debe tener la forma https://<id-del-proyecto>.supabase.co"
    if httpx.URL(url).path not in ("", "/"):
        return "no debe llevar ruta después de .supabase.co"
    return None


def _check(response: httpx.Response, action: str) -> None:
    if response.is_success:
        return
    # Never include headers (they carry the key); PostgREST error bodies are safe to show.
    raise HeartbeatError(f"{action}: HTTP {response.status_code} {response.text[:200]}")
