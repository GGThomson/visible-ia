"""Static checks on the SQL migrations (no database needed, runs in CI)."""

import re

from visible_ia.db import MIGRATIONS_DIR, migration_files

ALL_SQL = "\n".join(p.read_text(encoding="utf-8") for p in migration_files())

EXPECTED_TABLES = {
    "categories", "templates", "markets", "questions", "clinics", "clinic_markets",
    "aliases", "runs", "responses", "mentions", "sources", "monthly_scores", "clients",
    "sites", "app_users", "tasks", "reports", "prospects", "payments", "heartbeats",
}  # fmt: skip


def created_tables() -> set[str]:
    return set(re.findall(r"create table public\.(\w+)", ALL_SQL))


def rls_tables() -> set[str]:
    return set(re.findall(r"alter table public\.(\w+) enable row level security", ALL_SQL))


def test_migrations_are_numbered_and_unique():
    files = migration_files()
    assert files, f"no migrations found in {MIGRATIONS_DIR}"
    assert files[0].name == "0001_initial.sql"


def test_every_table_has_rls_enabled():
    missing = created_tables() - rls_tables()
    assert not missing, f"tables without RLS: {sorted(missing)}"


def test_expected_tables_exist():
    assert EXPECTED_TABLES <= created_tables()


def test_no_policies_in_initial_migration():
    # Policies arrive in later, dedicated migrations (C6, C7, C10).
    initial = (MIGRATIONS_DIR / "0001_initial.sql").read_text(encoding="utf-8").lower()
    assert "create policy" not in initial


def test_responses_have_purge_after():
    assert re.search(r"purge_after date not null default", ALL_SQL)
