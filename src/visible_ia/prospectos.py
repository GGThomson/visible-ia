"""Landing requests (prospects): the operator's list and the daily GitHub notice (C6-T04).

The Director learns about a new request within 24 h without opening Supabase: the daily job
opens or updates an issue "Prospectos nuevos (n)". The issue carries only the count and the
clinic names, never contact data (the repository is not the place for personal data).
`visible-ia prospectos nuevos` shows the contacts and marks them as seen; when none are left
unseen, the next daily run closes the issue.
"""

from dataclasses import dataclass
from datetime import datetime

import httpx
import psycopg

TITLE_PREFIX = "Prospectos nuevos"
GITHUB_API = "https://api.github.com"
CATEGORY_NAMES = {
    "IMP": "Implantología",
    "EDE": "Estética dental",
    "MES": "Medicina estética",
    "DER": "Dermatología",
}


@dataclass(frozen=True)
class Prospect:
    id: int
    created_at: datetime
    name: str
    clinic_name: str
    category_code: str | None
    district: str | None
    contact: str
    source: str | None


# --- operator (database) -------------------------------------------------------------------


def list_unseen(conn: psycopg.Connection) -> list[Prospect]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, created_at, name, clinic_name, category_code, district, contact, "
            "utm->>'utm_source' from public.prospects "
            "where not seen and not do_not_contact order by created_at"
        )
        return [Prospect(*row) for row in cur.fetchall()]


def mark_seen(conn: psycopg.Connection, ids: list[int]) -> None:
    if not ids:
        return
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("update public.prospects set seen = true where id = any(%s)", (ids,))


# --- daily notice (REST + GitHub) ----------------------------------------------------------


def unseen_clinics(
    supabase_url: str, service_role_key: str, client: httpx.Client | None = None
) -> list[str]:
    """Clinic names of unseen requests, read with the service role (RLS does not apply)."""
    own = client is None
    client = client or httpx.Client(timeout=20)
    headers = {"apikey": service_role_key, "Authorization": f"Bearer {service_role_key}"}
    try:
        response = client.get(
            f"{supabase_url}/rest/v1/prospects",
            params={
                "select": "clinic_name",
                "seen": "eq.false",
                "do_not_contact": "eq.false",
                "order": "created_at",
            },
            headers=headers,
        )
    finally:
        if own:
            client.close()
    response.raise_for_status()
    return [row["clinic_name"] for row in response.json()]


def issue_text(clinics: list[str]) -> tuple[str, str]:
    """Title and body of the notice: count and clinic names only, no contact data."""
    title = f"{TITLE_PREFIX} ({len(clinics)})"
    names = "\n".join(f"- {name}" for name in clinics)
    body = (
        f"Hay {len(clinics)} pedidos de informe gratis sin revisar:\n\n{names}\n\n"
        "Para ver los datos de contacto y marcarlos como vistos:\n\n"
        "```\nuv run visible-ia prospectos nuevos --env prod\n```\n\n"
        "_Este aviso no incluye datos de contacto a propósito. Se cierra solo cuando ya no quedan "
        "pedidos sin revisar._"
    )
    return title, body


def sync_issue(
    clinics: list[str], *, repo: str, token: str, client: httpx.Client | None = None
) -> str:
    """Open, update or close the notice issue. Returns what it did."""
    own = client is None
    client = client or httpx.Client(timeout=20)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    try:
        found = client.get(
            f"{GITHUB_API}/repos/{repo}/issues",
            params={"state": "open", "per_page": "100"},
            headers=headers,
        )
        found.raise_for_status()
        issue = next(
            (
                i
                for i in found.json()
                if i["title"].startswith(TITLE_PREFIX) and "pull_request" not in i
            ),
            None,
        )
        if not clinics:
            if issue is None:
                return "nada"
            client.patch(
                f"{GITHUB_API}/repos/{repo}/issues/{issue['number']}",
                json={"state": "closed"},
                headers=headers,
            ).raise_for_status()
            return "cerrado"
        title, body = issue_text(clinics)
        if issue is None:
            client.post(
                f"{GITHUB_API}/repos/{repo}/issues",
                json={"title": title, "body": body},
                headers=headers,
            ).raise_for_status()
            return "creado"
        client.patch(
            f"{GITHUB_API}/repos/{repo}/issues/{issue['number']}",
            json={"title": title, "body": body},
            headers=headers,
        ).raise_for_status()
        return "actualizado"
    finally:
        if own:
            client.close()
