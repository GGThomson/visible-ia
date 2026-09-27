"""Postgres connection and a minimal, ordered SQL migrator.

Migrations live in supabase/migrations/NNNN_name.sql and are applied in order, each one in
its own transaction. Applied versions are recorded in ops.schema_migrations (schema `ops` is
not exposed by the Supabase API).
"""

from pathlib import Path

import psycopg

from visible_ia.config import Env, Settings

MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "supabase" / "migrations"

BOOTSTRAP = """
create schema if not exists ops;
create table if not exists ops.schema_migrations (
    version text primary key,
    applied_at timestamptz not null default now()
);
"""


class MissingDatabaseUrl(RuntimeError):
    pass


def database_url(settings: Settings, env: Env) -> str:
    value = settings.value(f"SUPABASE_DB_URL_{env.upper()}")
    if value is None or not value.get_secret_value().strip():
        raise MissingDatabaseUrl(f"Falta SUPABASE_DB_URL_{env.upper()} en .env")
    return value.get_secret_value()


def connect(settings: Settings, env: Env, *, autocommit: bool = False) -> psycopg.Connection:
    """autocommit=True makes every `conn.transaction()` block a real, committed transaction:
    long commands (runs, extraction, review) must not lose paid work if they stop halfway."""
    return psycopg.connect(database_url(settings, env), connect_timeout=15, autocommit=autocommit)


def migration_files(directory: Path = MIGRATIONS_DIR) -> list[Path]:
    files = sorted(directory.glob("[0-9][0-9][0-9][0-9]_*.sql"))
    versions = [f.name[:4] for f in files]
    if len(versions) != len(set(versions)):
        raise ValueError("Hay dos migraciones con el mismo número")
    return files


def applied_versions(conn: psycopg.Connection) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(BOOTSTRAP)
        cur.execute("select version from ops.schema_migrations")
        return {row[0] for row in cur.fetchall()}


def pending_migrations(conn: psycopg.Connection, directory: Path = MIGRATIONS_DIR) -> list[Path]:
    done = applied_versions(conn)
    conn.commit()
    return [f for f in migration_files(directory) if f.name[:4] not in done]


def apply_migration(conn: psycopg.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(sql)
        cur.execute("insert into ops.schema_migrations (version) values (%s)", (path.name[:4],))
