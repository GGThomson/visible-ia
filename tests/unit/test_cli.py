from typer.testing import CliRunner

from visible_ia import __version__
from visible_ia.cli import app

runner = CliRunner()


def test_version_prints_package_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__ == "0.1.0"


def test_budget_rejects_unknown_surfaces_before_touching_the_database():
    result = runner.invoke(app, ["presupuesto", "ver", "--superficies", "chatgpt_app_manual"])
    assert result.exit_code == 2
    assert "Superficies no válidas" in result.stdout
