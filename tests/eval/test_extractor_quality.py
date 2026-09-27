"""Extractor quality gate (PRD §5.3) with the recorded LLM outputs: no API cost in CI.

Re-record after changing extractor/prompt.md:
    uv run python scripts/grabar_salidas_extractor.py   (≈ US$0.007, needs the Director's OK)
"""

import pytest

from visible_ia.extractor import evaluacion, llm


def test_quality_targets_on_confirmed_answers():
    gold = evaluacion.read_jsonl(evaluacion.GOLD)
    confirmed = [g for g in gold if g.get("estado") == "confirmada"]
    if not confirmed:
        pytest.skip("El Director aún no confirmó etiquetas (estado = 'confirmada')")
    outputs = evaluacion.load_outputs()
    if not outputs:
        pytest.skip("Faltan las salidas grabadas del extractor (data/eval/extractor-salidas.jsonl)")
    recorded_versions = {
        row.get("extractor_version") for row in evaluacion.read_jsonl(evaluacion.OUTPUTS)
    }
    assert recorded_versions == {llm.load_prompt().extractor_version}, (
        "Las salidas grabadas son de otra versión del prompt: vuelve a grabarlas"
    )

    scores = evaluacion.score(gold, outputs)
    print("\n" + scores.report())
    assert not scores.errors, scores.errors
    assert len(confirmed) >= 60, f"Hay {len(confirmed)} respuestas confirmadas (meta: ≥ 60)"
    assert not scores.failing(), f"No cumple las metas del PRD §5.3: {scores.report()}"
