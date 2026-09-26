"""Command line interface for the operator."""

import typer

from visible_ia import __version__

app = typer.Typer(help="visible-ia: herramienta del operador.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """visible-ia: herramienta del operador."""


@app.command()
def version() -> None:
    """Muestra la versión instalada."""
    typer.echo(__version__)
