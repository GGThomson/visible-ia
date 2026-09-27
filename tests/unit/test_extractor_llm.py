import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from visible_ia.extractor import llm
from visible_ia.motor import chatgpt_api, google_ai_mode

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _json(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


CHATGPT_TEXT = chatgpt_api.parse_response(_json("openai_response_real.json")).text
GOOGLE_RAW = _json("serpapi_ai_mode_real.json")
GOOGLE_TEXT = google_ai_mode.parse_response(GOOGLE_RAW).text
NANO = _json("extractor_nano_response.json")


def test_prompt_is_versioned():
    prompt = llm.load_prompt()
    assert prompt.version == "2"
    assert prompt.extractor_version == "gpt-5-nano/prompt-v2"
    assert not prompt.text.startswith("<!--") and "solo el nombre" in prompt.text


def test_parse_keeps_literal_clinics_in_text_order():
    result = llm.parse_response(NANO, CHATGPT_TEXT)
    assert [(m.position, m.raw_name) for m in result.mentions] == [
        (1, "The Dental Clinic & GT Concept Asociados"),
        (2, "Odontonova"),
        (3, "Clínica Miraflores"),
        (4, "V&C Odontólogos"),
    ]
    assert result.extractor_version == "gpt-5-nano/prompt-v2"


def test_invented_names_and_platforms_are_discarded():
    result = llm.parse_response(NANO, CHATGPT_TEXT)
    # "Smiles Peru" is not in this answer; Doctoralia is a platform even if flagged as clinic.
    assert result.discarded == ["Smiles Peru", "limadentalrating.com", "Doctoralia"]


def test_cost_is_within_the_target_per_answer():
    result = llm.parse_response(NANO, CHATGPT_TEXT)
    # 1800 × 0.05 / 1e6 + 220 × 0.40 / 1e6
    assert result.cost_usd == pytest.approx(0.000178)
    assert result.cost_usd <= 0.0005


def test_validation_ignores_case_accents_and_spacing():
    candidates = [
        {
            "nombre_tal_cual": "dental perez  yance",
            "orden": 1,
            "es_establecimiento_o_profesional": True,
        },
        {
            "nombre_tal_cual": "Dr. Aldo Implants",
            "orden": 2,
            "es_establecimiento_o_profesional": True,
        },
    ]
    mentions, discarded = llm.validate(candidates, GOOGLE_TEXT)
    assert [m.raw_name for m in mentions] == ["Dr. Aldo Implants", "dental perez  yance"]
    assert discarded == []


def test_partial_words_do_not_count_as_literal():
    candidates = [{"nombre_tal_cual": "Nova", "orden": 1, "es_establecimiento_o_profesional": True}]
    mentions, discarded = llm.validate(candidates, "Te recomiendo Odontonova.")
    assert mentions == [] and discarded == ["Nova"]


def test_name_only_in_link_texts_is_kept_after_text_mentions():
    candidates = [
        {"nombre_tal_cual": "Clínica Enlace", "orden": 1, "es_establecimiento_o_profesional": True},
        {"nombre_tal_cual": "Clínica Texto", "orden": 2, "es_establecimiento_o_profesional": True},
    ]
    mentions, _ = llm.validate(candidates, "Ve a Clínica Texto.", ["Clínica Enlace"])
    assert [m.raw_name for m in mentions] == ["Clínica Texto", "Clínica Enlace"]


def test_google_link_texts_come_from_snippet_links():
    assert llm.link_texts_from_raw("google_ai_mode", GOOGLE_RAW) == [
        "Dr. Aldo Implants",
        "Dental Pérez Yance",
        "Implantes Dentales Miraflores",
    ]
    assert llm.link_texts_from_raw("chatgpt_api", GOOGLE_RAW) == []


def test_build_input_adds_link_texts_section():
    text = llm.build_input("Respuesta X", ["Dental Pérez Yance"])
    assert text == "Respuesta:\nRespuesta X\n\nTextos de enlaces:\n- Dental Pérez Yance"


class FakeClient:
    def __init__(self, raw):
        self.raw = raw
        self.calls = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(model_dump=lambda mode: self.raw)


def test_request_uses_nano_strict_schema_and_minimal_reasoning():
    client = FakeClient(NANO)
    llm.extract(CHATGPT_TEXT, client=client)
    call = client.calls[0]
    assert call["model"] == "gpt-5-nano"
    assert call["reasoning"] == {"effort": "minimal"}
    assert call["text"]["format"]["strict"] is True
    assert call["text"]["format"]["schema"] == llm.SCHEMA
    assert call["instructions"] == llm.load_prompt().text
    assert "temperature" not in call


def test_empty_answer_makes_no_call():
    client = FakeClient(NANO)
    result = llm.extract("   ", client=client)
    assert result.mentions == [] and client.calls == []


def test_missing_output_is_an_error():
    raw = {"output": [{"type": "message", "content": [{"type": "refusal", "refusal": "no"}]}]}
    with pytest.raises(ValueError, match="no devolvió salida"):
        llm.parse_response(raw, "texto")


@pytest.mark.live
def test_live_extraction_of_recorded_answers():
    """2 real gpt-5-nano calls (≈ US$0.0005). Run: uv run pytest -m live -k extraction -s"""
    from visible_ia.config import get_settings

    key = get_settings().openai_api_key
    if key is None:
        pytest.skip("Falta OPENAI_API_KEY")
    out = {}
    for name, text, links in [
        ("chatgpt", CHATGPT_TEXT, None),
        ("google", GOOGLE_TEXT, llm.link_texts_from_raw("google_ai_mode", GOOGLE_RAW)),
    ]:
        result = llm.extract(text, link_texts=links, api_key=key.get_secret_value())
        print(f"\n{name}: {[m.raw_name for m in result.mentions]}")
        print(f"  descartados={result.discarded} costo=US${result.cost_usd:.6f} uso={result.usage}")
        out[name] = result.raw
        assert result.mentions
    if os.environ.get("SAVE_LIVE_FIXTURE"):
        (FIXTURES / "extractor_nano_live.json").write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )
