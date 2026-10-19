"""Safety net for the repo reorganization (acta 2026-09-29-mapa-del-sistema, step 1).

Moving files must not change what the CLI does:
1. The tree of commands and options stays exactly as in `cli_comandos.txt`.
2. Every `from visible_ia... import ...` in src/ and scripts/ resolves, including the imports
   inside functions (cli.py imports lazily, so a broken path would only fail when the command
   runs).
3. Every `visible-ia ...` command called by the GitHub workflows exists.

To accept an intended change of commands: `UPDATE_CLI_SNAPSHOT=1 pytest tests/unit/test_red_cli.py`.
"""

import ast
import importlib
import os
import re
from pathlib import Path

import pytest
import typer

from visible_ia.cli import app

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = Path(__file__).with_name("cli_comandos.txt")


def _tree(command, path=()):
    if hasattr(command, "commands"):  # a group
        for name, sub in sorted(command.commands.items()):
            yield from _tree(sub, (*path, name))
        return
    params = []
    for p in command.params:
        kind = "arg" if "Argument" in type(p).__name__ else "opt"
        names = "/".join([*p.opts, *getattr(p, "secondary_opts", [])])
        params.append(f"{kind}:{names}{'*' if p.required else ''}")
    yield " ".join(path) + " | " + " ".join(params)


def command_tree() -> list[str]:
    return list(_tree(typer.main.get_command(app)))


def test_command_tree_is_unchanged():
    current = "\n".join(command_tree()) + "\n"
    if os.environ.get("UPDATE_CLI_SNAPSHOT"):
        SNAPSHOT.write_text(current, encoding="utf-8")
    assert current == SNAPSHOT.read_text(encoding="utf-8"), (
        "Cambió un comando o una opción del CLI. Si es a propósito: UPDATE_CLI_SNAPSHOT=1"
    )


def _own_imports():
    files = [*(ROOT / "src" / "visible_ia").rglob("*.py"), *(ROOT / "scripts").glob("*.py")]
    for path in files:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("visible_ia"):
                for alias in node.names:
                    yield path.relative_to(ROOT).as_posix(), node.module, alias.name


@pytest.mark.parametrize("where, module, name", sorted(set(_own_imports())))
def test_every_internal_import_resolves(where, module, name):
    imported = importlib.import_module(module)
    if name != "*" and not hasattr(imported, name):
        importlib.import_module(f"{module}.{name}")  # a submodule (from pkg import module)


def test_every_command_the_workflows_call_exists():
    commands = {line.split(" | ")[0] for line in command_tree()}
    groups = {c.split(" ")[0] for c in commands}
    called = []
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        for m in re.finditer(r"visible-ia ((?:[a-z][\w-]* ?)+)", workflow.read_text("utf-8")):
            words = m.group(1).split()
            # "mensual ${{ inputs.modo }}" leaves only the group: check the group then.
            called.append(" ".join(words[:2]) if len(words) > 1 else words[0])
    assert called, "no se encontraron llamadas a visible-ia en los workflows"
    for c in called:
        assert c in commands or c in groups, f"un workflow llama a «visible-ia {c}», que no existe"
