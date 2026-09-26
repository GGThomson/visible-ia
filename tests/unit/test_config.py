import pytest
from typer.testing import CliRunner

from visible_ia.cli import app

runner = CliRunner()

FAKE = {
    "SUPABASE_URL_DEV": "https://dev-fake.supabase.co",
    "SUPABASE_ANON_KEY_DEV": "anon-dev-SECRET-123",
    "SUPABASE_SERVICE_ROLE_KEY_DEV": "service-dev-SECRET-456",
    "OPENAI_API_KEY": "sk-openai-SECRET-789",
    "CLOUDFLARE_API_TOKEN": "cf-SECRET-000",
}
ALL_VARS = [
    "VISIBLE_IA_ENV",
    *(
        f"{b}_{e}"
        for b in (
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_DB_URL",
        )
        for e in ("DEV", "PROD")
    ),
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_API_TOKEN",
    "OPENAI_API_KEY",
    "SERPAPI_API_KEY",
]


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path):
    # Never read the developer's real .env during tests.
    monkeypatch.chdir(tmp_path)
    for name in ALL_VARS:
        monkeypatch.delenv(name, raising=False)


def test_missing_required_fails_and_names_variables():
    result = runner.invoke(app, ["config", "check"])
    assert result.exit_code == 1
    assert "FALTA (obligatoria): SUPABASE_URL_DEV" in result.stdout
    assert "SUPABASE_SERVICE_ROLE_KEY_DEV" in result.stdout


def test_ok_when_required_present_and_never_prints_values(monkeypatch):
    for k, v in FAKE.items():
        monkeypatch.setenv(k, v)
    result = runner.invoke(app, ["config", "check"])
    assert result.exit_code == 0
    assert "OK" in result.stdout
    for v in FAKE.values():
        assert v not in result.stdout
    assert "SUPABASE_DB_URL_DEV -> se necesita en C1-T03" in result.stdout


def test_prod_checked_separately(monkeypatch):
    for k, v in FAKE.items():
        monkeypatch.setenv(k, v)
    result = runner.invoke(app, ["config", "check", "--env", "prod"])
    assert result.exit_code == 1
    assert "SUPABASE_URL_PROD" in result.stdout


def test_invalid_env_rejected():
    result = runner.invoke(app, ["config", "check", "--env", "staging"])
    assert result.exit_code == 2


def test_env_example_lists_every_variable():
    from pathlib import Path

    example = (Path(__file__).parents[2] / ".env.example").read_text(encoding="utf-8")
    for name in ALL_VARS:
        assert f"{name}=" in example
