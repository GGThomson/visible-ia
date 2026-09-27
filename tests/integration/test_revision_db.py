import csv
from datetime import date

import pytest

from visible_ia.extractor import llm
from visible_ia.extractor.extraccion import extract_run, pending_answers
from visible_ia.extractor.revision import (
    ReviewError,
    apply_csv,
    close_review,
    export_csv,
    new_clinics,
    run_mentions,
)
from visible_ia.mercados.clinicas import ClinicRow, import_clinics
from visible_ia.mercados.mercado import create_market, list_questions
from visible_ia.motor.corrida import Call, create_run, save_response
from visible_ia.motor.modelos import Citation, EngineResponse

pytestmark = pytest.mark.integration

ANSWER = "Te recomiendo Dental Pérez Yance y Smiles. También Odontonova y Clínica Nueva Sonrisa X."


def _setup(tx):
    market = create_market(tx, "DER", "Surco")
    import_clinics(
        tx,
        market,
        [
            ClinicRow(
                name="Implantes Dental | Perez Yance / Clínicas Dentales Americadent",
                district="Surco",
                maps_url="https://maps.google.com/?cid=test-rev-1",
                website="https://dentalperezyance.com/",
            ),
            ClinicRow(
                name="Smiles Peru",
                district="Surco",
                maps_url="https://maps.google.com/?cid=test-rev-2",
            ),
            ClinicRow(
                name="Digital Smiles",
                district="Surco",
                maps_url="https://maps.google.com/?cid=test-rev-3",
            ),
        ],
        date(2026, 9, 26),
    )
    run_id = create_run(
        tx, market, surfaces=["chatgpt_api"], repetitions=1, estimated_cost_usd=0, forced=False
    )
    q = list_questions(tx, market)[0]
    answer = EngineResponse(
        surface="chatgpt_api",
        provider="fake",
        text=ANSWER,
        citations=[
            Citation(url="https://dentalperezyance.com/implantes"),
            Citation(url="https://www.doctoralia.pe/x"),
        ],
    )
    save_response(tx, run_id, Call(q.id, q.template_id, q.text, "chatgpt_api", 1), answer)
    return market, run_id


def fake_extractor(text, links):
    names = ["Dental Pérez Yance", "Smiles", "Odontonova", "Clínica Nueva Sonrisa X"]
    return llm.Extraction(
        mentions=[llm.Mention(n, i) for i, n in enumerate(names, start=1)],
        cost_usd=0.0002,
        extractor_version="gpt-5-nano/prompt-v1",
    )


def test_extract_matches_classifies_and_is_not_repeated(tx):
    market, run_id = _setup(tx)
    summary = extract_run(tx, run_id, fake_extractor)

    assert (summary.extracted, summary.mentions) == (1, 4)
    assert (summary.matched, summary.new, summary.review) == (1, 2, 1)
    rows = {r.raw_name: r for r in run_mentions(tx, run_id)}
    assert rows["Dental Pérez Yance"].clinic_name.startswith("Implantes Dental | Perez Yance")
    assert rows["Smiles"].status == "review"  # tie between Smiles Peru and Digital Smiles
    assert rows["Odontonova"].clinic_id is None and rows["Odontonova"].status == "auto"
    with tx.cursor() as cur:
        cur.execute(
            "select s.domain, s.source_type from public.sources s join public.responses r "
            "on r.id = s.response_id where r.run_id = %s order by 1",
            (run_id,),
        )
        assert cur.fetchall() == [
            ("dentalperezyance.com", "own_website"),
            ("doctoralia.pe", "doctoralia"),
        ]
        cur.execute(
            "select extractor_version, extraction_cost_usd from public.responses where run_id = %s",
            (run_id,),
        )
        version, cost = cur.fetchone()
        assert version == "gpt-5-nano/prompt-v1" and float(cost) == pytest.approx(0.0002)

    assert pending_answers(tx, run_id) == []
    assert extract_run(tx, run_id, fake_extractor).extracted == 0


def test_review_from_csv_applies_every_action(tx, tmp_path):
    market, run_id = _setup(tx)
    extract_run(tx, run_id, fake_extractor)
    with tx.cursor() as cur:
        cur.execute("select id from public.clinics where name = 'Smiles Peru'")
        (smiles_id,) = cur.fetchone()

    assert [name for name, _, _ in new_clinics(tx, market)] == [
        "Clínica Nueva Sonrisa X",
        "Odontonova",
    ]
    with pytest.raises(ReviewError, match="revisión"):
        close_review(tx, run_id)

    path = tmp_path / "revision.csv"
    assert export_csv(tx, run_id, path) == 4
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    by_name = {r["raw_name"]: r for r in rows}
    by_name["Smiles"].update(accion="asociar", clinica_destino=str(smiles_id))
    by_name["Odontonova"].update(accion="nueva", nombre_nueva="Odontonova Centro de Implantología")
    by_name["Clínica Nueva Sonrisa X"].update(accion="descartar")
    by_name["Dental Pérez Yance"].update(accion="ok")
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    result = apply_csv(tx, run_id, path)
    assert result.errors == []
    assert dict(result.by_action) == {"asociar": 1, "nueva": 1, "descartar": 1, "ok": 1}

    after = {r.raw_name: r for r in run_mentions(tx, run_id)}
    assert (after["Smiles"].clinic_id, after["Smiles"].status) == (smiles_id, "corrected")
    assert after["Odontonova"].clinic_name == "Odontonova Centro de Implantología"
    assert after["Odontonova"].status == "corrected"
    assert after["Clínica Nueva Sonrisa X"].status == "discarded"
    assert after["Dental Pérez Yance"].status == "auto"
    assert new_clinics(tx, market) == []

    close_review(tx, run_id)
    with tx.cursor() as cur:
        cur.execute("select status from public.runs where id = %s", (run_id,))
        assert cur.fetchone()[0] == "reviewed"
        # The new clinic keeps the name used in the answer as an alias.
        cur.execute(
            "select a.alias from public.aliases a join public.clinics c on c.id = a.clinic_id "
            "where c.name = 'Odontonova Centro de Implantología'"
        )
        assert "Odontonova" in {row[0] for row in cur.fetchall()}


def test_merge_keeps_the_earlier_position_and_bad_rows_are_reported(tx):
    market, run_id = _setup(tx)
    extract_run(tx, run_id, fake_extractor)
    rows = {r.raw_name: r for r in run_mentions(tx, run_id)}
    first, later = rows["Dental Pérez Yance"], rows["Odontonova"]

    result = apply_csv_rows(tx, run_id, [
        {"mention_id": str(first.mention_id), "accion": "unir", "unir_con": str(later.mention_id)},
        {"mention_id": str(later.mention_id), "accion": "volar"},
        {"mention_id": "999999999", "accion": "descartar"},
        {"mention_id": str(rows["Smiles"].mention_id), "accion": "ok"},
    ])  # fmt: skip
    assert result.by_action == {"unir": 1}
    assert len(result.errors) == 3
    after = {r.mention_id: r for r in run_mentions(tx, run_id)}
    assert after[later.mention_id].position == 1
    assert after[first.mention_id].status == "discarded"


def apply_csv_rows(tx, run_id, rows):
    from visible_ia.extractor.revision import apply_corrections

    return apply_corrections(tx, run_id, rows)


def test_reassociate_after_the_clinic_list_grows(tx):
    market, run_id = _setup(tx)
    extract_run(tx, run_id, fake_extractor)
    from visible_ia.extractor.revision import discard, reassociate

    rows = {r.raw_name: r for r in run_mentions(tx, run_id)}
    discard(tx, run_id, rows["Clínica Nueva Sonrisa X"].mention_id)
    import_clinics(
        tx,
        market,
        [
            ClinicRow(
                name="Odontonova",
                district="Surco",
                maps_url="https://maps.google.com/?cid=test-rev-4",
                aliases=("Odontonova Centro",),
            ),
            ClinicRow(
                name="Nueva Sonrisa X",
                district="Surco",
                maps_url="https://maps.google.com/?cid=test-rev-5",
            ),
        ],
        date(2026, 9, 27),
    )
    counts = reassociate(tx, run_id)
    after = {r.raw_name: r for r in run_mentions(tx, run_id)}
    assert after["Odontonova"].clinic_name == "Odontonova"
    assert after["Clínica Nueva Sonrisa X"].status == "discarded"  # manual decisions stay
    assert after["Clínica Nueva Sonrisa X"].clinic_id is None
    assert counts["changed"] == 1
