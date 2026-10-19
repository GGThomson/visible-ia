"""The only place that knows where the repo's files live (reorganization step 3, 19/10/2026).

Modules ask here instead of climbing folders with `Path(__file__).parents[n]`, so a module can
move without silently losing its data. Each niche keeps its files in `config/nichos/<niche>/`.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"  # not niche-specific: rates, evaluation, phase-1 sample
OUTPUT_DIR = REPO_ROOT / "salida"
MIGRATIONS_DIR = REPO_ROOT / "supabase" / "migrations"
NICHES_DIR = Path(__file__).resolve().parent / "nichos"
DEFAULT_NICHE = "dental"  # Eminia; the only niche configured so far


def niche_file(name: str, niche: str = DEFAULT_NICHE) -> Path:
    """A configuration file of a niche, e.g. niche_file("preguntas.csv")."""
    return NICHES_DIR / niche / name
