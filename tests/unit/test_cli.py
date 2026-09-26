from typer.testing import CliRunner

from visible_ia import __version__
from visible_ia.cli import app

runner = CliRunner()


def test_version_prints_package_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__ == "0.1.0"
