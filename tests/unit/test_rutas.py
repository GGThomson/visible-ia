"""Single path loader (reorganization step 3): every file the code reads is where `rutas` says,
and no module climbs folders on its own, so moving a module cannot lose its data silently."""

import re

import pytest

from visible_ia.config import rutas
from visible_ia.config.rutas import DATA_DIR, MIGRATIONS_DIR, REPO_ROOT, niche_file

NICHE_FILES = ["nicho.toml", "preguntas.csv", "recomendaciones.toml", "semaforo.toml",
               "checklist.toml", "dominios.csv"]  # fmt: skip


def test_repo_root_is_the_repo():
    assert (REPO_ROOT / "pyproject.toml").is_file() and MIGRATIONS_DIR.is_dir()


@pytest.mark.parametrize("name", NICHE_FILES)
def test_every_file_of_the_dental_niche_exists(name):
    assert niche_file(name).is_file(), niche_file(name)


@pytest.mark.parametrize("name", ["tarifas.toml", "fase1-preguntas.csv", "eval"])
def test_shared_data_stays_in_data(name):
    assert (DATA_DIR / name).exists()


def test_the_modules_read_through_rutas():
    from visible_ia import checklist, db
    from visible_ia.config import nichos
    from visible_ia.extractor import evaluacion, fuentes
    from visible_ia.informes import contexto, pdf, semaforo
    from visible_ia.mercados import plantillas
    from visible_ia.motor import manual, tarifas

    assert nichos.NICHE_TOML == niche_file("nicho.toml")
    assert plantillas.TEMPLATES_CSV == niche_file("preguntas.csv")
    assert contexto.RECOMMENDATIONS_TOML == niche_file("recomendaciones.toml")
    assert semaforo.RULES_TOML == niche_file("semaforo.toml")
    assert checklist.CATALOG == niche_file("checklist.toml")
    assert fuentes.DOMAINS_CSV == niche_file("dominios.csv")
    assert db.MIGRATIONS_DIR == MIGRATIONS_DIR and pdf.OUTPUT_DIR == rutas.OUTPUT_DIR
    assert tarifas.RATES_TOML.is_file() and manual.PHASE1_QUESTIONS_CSV.is_file()
    assert evaluacion.EVAL_DIR.is_dir()


def test_no_module_climbs_folders_but_rutas():
    src = REPO_ROOT / "src" / "visible_ia"
    offenders = [
        p.relative_to(src).as_posix()
        for p in src.rglob("*.py")
        if p.name != "rutas.py" and re.search(r"\.parents\[\d\]", p.read_text(encoding="utf-8"))
    ]
    assert offenders == [], f"usa visible_ia.config.rutas en vez de parents[n]: {offenders}"
