"""Clients, their sites (clinic x market) and panel users (C7-T01, HU-19).

A client is a clinic or an agency; a clinic client can have several sites. A panel user is a
Supabase Auth user linked to exactly one client (public.app_users). Inviting an e-mail that
already exists never duplicates the user: it is looked up in auth.users first.

Two ways to invite:
- by e-mail: Supabase sends the invitation (new user) or a sign-in link (existing user);
  needs an SMTP provider for addresses outside the Supabase team;
- `link_only`: Supabase generates the sign-in link without sending anything, and the
  operator sends it by WhatsApp.
"""

from dataclasses import dataclass

import httpx
import psycopg

KINDS = ("clinic", "agency")
PANEL_PATH = "/panel/"


class ClientError(ValueError):
    pass


@dataclass(frozen=True)
class Invitation:
    user_id: str
    email: str
    created: bool  # False when the user already existed
    link: str | None  # only with link_only


def normalize_email(email: str) -> str:
    email = email.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1] or " " in email:
        raise ClientError(f"Correo no válido: {email}")
    return email


# --- database ------------------------------------------------------------------------------


def create_client(
    conn: psycopg.Connection,
    kind: str,
    name: str,
    *,
    email: str | None = None,
    phone: str | None = None,
    agency_id: int | None = None,
) -> int:
    if kind not in KINDS:
        raise ClientError(f"Tipo no válido: {kind} (usa clinic o agency)")
    if not name.strip():
        raise ClientError("El nombre no puede estar vacío")
    with conn.transaction(), conn.cursor() as cur:
        if agency_id is not None:
            cur.execute("select kind from public.clients where id = %s", (agency_id,))
            row = cur.fetchone()
            if row is None or row[0] != "agency":
                raise ClientError(f"El cliente {agency_id} no es una agencia")
        cur.execute(
            "insert into public.clients (kind, name, contact_email, contact_phone, "
            "parent_agency_id) values (%s, %s, %s, %s, %s) returning id",
            (kind, name.strip(), normalize_email(email) if email else None, phone, agency_id),
        )
        return cur.fetchone()[0]


def add_site(
    conn: psycopg.Connection, client_id: int, clinic_id: int, market_id: int
) -> tuple[int, bool]:
    """Link a clinic of a market to the client. Returns (site_id, created)."""
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("select 1 from public.clients where id = %s", (client_id,))
        if cur.fetchone() is None:
            raise ClientError(f"No existe el cliente {client_id}")
        cur.execute(
            "select 1 from public.clinic_markets where clinic_id = %s and market_id = %s",
            (clinic_id, market_id),
        )
        if cur.fetchone() is None:
            raise ClientError(f"La clínica {clinic_id} no está en el mercado {market_id}")
        cur.execute(
            "select id from public.sites where client_id = %s and clinic_id = %s "
            "and market_id = %s and active_to is null",
            (client_id, clinic_id, market_id),
        )
        row = cur.fetchone()
        if row:
            return row[0], False
        cur.execute(
            "insert into public.sites (client_id, clinic_id, market_id) values (%s, %s, %s) "
            "returning id",
            (client_id, clinic_id, market_id),
        )
        return cur.fetchone()[0], True


def find_user(conn: psycopg.Connection, email: str) -> str | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id::text from auth.users where lower(email) = %s", (normalize_email(email),)
        )
        row = cur.fetchone()
    return row[0] if row else None


def link_user(conn: psycopg.Connection, user_id: str, client_id: int) -> None:
    """Attach an auth user to a client. A user belongs to one client only."""
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("select kind from public.clients where id = %s", (client_id,))
        row = cur.fetchone()
        if row is None:
            raise ClientError(f"No existe el cliente {client_id}")
        role = row[0]
        cur.execute("select client_id from public.app_users where id = %s", (user_id,))
        existing = cur.fetchone()
        if existing and existing[0] != client_id:
            raise ClientError(f"Ese usuario ya pertenece al cliente {existing[0]}")
        cur.execute(
            "insert into public.app_users (id, client_id, role) values (%s, %s, %s) "
            "on conflict (id) do nothing",
            (user_id, client_id, role),
        )


def list_clients(conn: psycopg.Connection) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            "select c.id, c.kind, c.name, c.status, "
            "count(distinct s.id) filter (where s.active_to is null), count(distinct u.id) "
            "from public.clients c left join public.sites s on s.client_id = c.id "
            "left join public.app_users u on u.client_id = c.id group by c.id order by c.id"
        )
        return cur.fetchall()


# --- Supabase Auth (admin API, service role) -----------------------------------------------


class AuthAdmin:
    def __init__(
        self, supabase_url: str, service_role_key: str, client: httpx.Client | None = None
    ):
        self.url = supabase_url.rstrip("/")
        self.headers = {"apikey": service_role_key, "Authorization": f"Bearer {service_role_key}"}
        self.client = client or httpx.Client(timeout=30)

    def _post(self, path: str, payload: dict) -> dict:
        response = self.client.post(f"{self.url}/auth/v1{path}", json=payload, headers=self.headers)
        if response.status_code >= 300:
            raise ClientError(
                f"Supabase Auth respondió {response.status_code}: {response.text[:200]}"
            )
        return response.json() if response.content else {}

    def invite(self, email: str, redirect_to: str) -> str:
        """New user + invitation e-mail. Returns the user id."""
        return self._post("/invite", {"email": email, "redirect_to": redirect_to})["id"]

    def send_sign_in(self, email: str, redirect_to: str) -> None:
        """Existing user: e-mail a sign-in link (never creates a user)."""
        self._post(f"/otp?redirect_to={redirect_to}", {"email": email, "create_user": False})

    def generate_link(self, email: str, redirect_to: str, *, new: bool) -> tuple[str, str]:
        """Sign-in link without sending e-mail. Returns (user_id, link)."""
        data = self._post(
            "/admin/generate_link",
            {"type": "invite" if new else "magiclink", "email": email, "redirect_to": redirect_to},
        )
        user = data.get("user") or data
        link = data.get("action_link") or (data.get("properties") or {}).get("action_link")
        if not link:
            raise ClientError("Supabase no devolvió el enlace")
        return user["id"], link

    def delete_user(self, user_id: str) -> None:
        self.client.delete(f"{self.url}/auth/v1/admin/users/{user_id}", headers=self.headers)


def invite_user(
    conn: psycopg.Connection,
    auth: AuthAdmin,
    client_id: int,
    email: str,
    *,
    site_url: str,
    link_only: bool = False,
) -> Invitation:
    email = normalize_email(email)
    redirect_to = site_url.rstrip("/") + PANEL_PATH
    user_id = find_user(conn, email)
    created = user_id is None
    link = None
    if link_only:
        user_id, link = auth.generate_link(email, redirect_to, new=created)
    elif created:
        user_id = auth.invite(email, redirect_to)
    else:
        auth.send_sign_in(email, redirect_to)
    link_user(conn, user_id, client_id)
    return Invitation(user_id, email, created, link)
