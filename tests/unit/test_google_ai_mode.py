import json
import os
from pathlib import Path

import httpx
import pytest

from visible_ia.motor import google_ai_mode

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "serpapi_ai_mode.json"
REAL = FIXTURE.with_name("serpapi_ai_mode_real.json")


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_parse_rebuilds_text_from_blocks_in_order():
    result = google_ai_mode.parse_response(load_fixture())

    assert result.surface == "google_ai_mode"
    assert result.provider == "serpapi"
    assert result.text.splitlines() == [
        "En Miraflores hay varias clínicas con experiencia en implantes dentales:",
        "- Clínica Dental Sonrisa Andina: tomografía propia y garantía de 5 años.",
        "- Centro Odontológico Larco: atiende sábados y ofrece financiamiento.",
        "  - Evaluación inicial gratuita.",
        "## Consejos",
        "Revisa las reseñas en Doctoralia antes de decidir.",
    ]
    assert result.searches == 1 and result.cost_usd == 0 and not result.empty


def test_parse_takes_references_without_duplicates():
    result = google_ai_mode.parse_response(load_fixture())
    assert [c.url for c in result.citations] == [
        "https://www.sonrisaandina.pe/implantes",
        "https://www.facebook.com/odontologicolarco",
        "https://www.doctoralia.pe/implantologia/miraflores",
    ]
    assert result.citations[2].title == "Implantólogos en Miraflores - Doctoralia"


def test_markdown_is_the_fallback_without_blocks_and_drops_references():
    raw = {
        "text_blocks": [],
        "reconstructed_markdown": "1. **Sonrisa Andina**\n2. Larco\n\n### References\n\n[0] x",
    }
    assert google_ai_mode.parse_response(raw).text == "1. **Sonrisa Andina**\n2. Larco"


def test_real_answer_drops_card_buttons_and_keeps_clinic_websites():
    """Recorded on 2026-09-26 from the verification call (C3-T02)."""
    raw = json.loads(REAL.read_text(encoding="utf-8"))
    result = google_ai_mode.parse_response(raw)

    assert "Llamar" not in result.text and "Cómo llegar" not in result.text
    assert "### References" not in result.text
    assert result.text.splitlines()[1].startswith("Destacado por su alta puntuación")
    urls = [c.url for c in result.citations]
    assert urls[:3] == [
        "https://www.tusimplantesdentalesmiraflores.com/",
        "https://dentalperezyance.com/",
        "https://www.implantesdentalesmiraflores.com/",
    ]
    assert len(urls) == 6  # 3 inline links + 3 references (Google viewer URLs)
    assert raw["search_parameters"]["location_used"] == "Lima Province,Peru"


def test_raw_drops_metadata_urls():
    raw = google_ai_mode.parse_response(load_fixture()).raw
    assert "json_endpoint" not in raw["search_metadata"]
    assert raw["search_metadata"]["id"] == "fixture0001"


def test_no_ai_answer_is_an_empty_marked_response_not_an_error():
    raw = {
        "search_metadata": {"status": "Success"},
        "error": "Google hasn't returned any results for this query.",
    }
    result = google_ai_mode.parse_response(raw)
    assert result.empty and result.text == "" and result.citations == []
    assert result.searches == 1


def test_other_serpapi_errors_raise():
    with pytest.raises(google_ai_mode.SerpApiError, match="run out"):
        google_ai_mode.parse_response({"error": "Your account has run out of searches."})


def _client(responses, seen):
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return queue.pop(0)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_request_params_lima_spanish_and_no_cache():
    seen = []
    client = _client([httpx.Response(200, json=load_fixture())], seen)
    google_ai_mode.ask("¿Implantes en Miraflores?", api_key="k", client=client)

    params = dict(seen[0].url.params)
    assert params == {
        "engine": "google_ai_mode",
        "q": "¿Implantes en Miraflores?",
        "location": "Lima, Peru",
        "hl": "es",
        "gl": "pe",
        "no_cache": "true",
        "api_key": "k",
    }


def test_429_and_5xx_are_retried_then_succeed():
    seen, waits = [], []
    client = _client(
        [httpx.Response(429), httpx.Response(502), httpx.Response(200, json=load_fixture())], seen
    )
    result = google_ai_mode.ask("q", api_key="k", client=client, sleep=waits.append)
    assert result.text and len(seen) == 3 and waits == [2, 4]


def test_gives_up_after_three_retries():
    seen, waits = [], []
    client = _client([httpx.Response(503)] * 4, seen)
    with pytest.raises(google_ai_mode.SerpApiError, match="503"):
        google_ai_mode.ask("q", api_key="k", client=client, sleep=waits.append)
    assert len(seen) == 4 and waits == [2, 4, 8]


def test_401_propagates_without_retry():
    seen, waits = [], []
    client = _client([httpx.Response(401, json={"error": "Invalid API key."})], seen)
    with pytest.raises(google_ai_mode.SerpApiError, match="Invalid API key"):
        google_ai_mode.ask("q", api_key="k", client=client, sleep=waits.append)
    assert len(seen) == 1 and waits == []


@pytest.mark.live
def test_live_single_call():
    """One real search (1 SerpApi credit). Run with: uv run pytest -m live -k google -s"""
    from visible_ia.config import get_settings

    key = get_settings().serpapi_api_key
    if key is None:
        pytest.skip("Falta SERPAPI_API_KEY")
    result = google_ai_mode.ask(
        "¿Qué clínica me recomiendas para implantes dentales en Miraflores?",
        api_key=key.get_secret_value(),
    )
    if os.environ.get("SAVE_LIVE_FIXTURE"):
        out = FIXTURE.with_name("serpapi_ai_mode_live.json")
        out.write_text(json.dumps(result.raw, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nubicación={result.raw.get('search_parameters', {}).get('location_used')}")
    print(f"vacía={result.empty} fuentes={len(result.citations)}")
    print(result.text[:500])
    assert result.raw.get("search_metadata", {}).get("status") == "Success"


def test_identical_consecutive_blocks_are_kept_once():
    card = {
        "type": "list",
        "list": [
            {"snippet": "Ubicación: Av. José Pardo 434, Miraflores."},
            {
                "snippet": "Referencia: más detalles en Dental Pérez Yance.",
                "snippet_links": [
                    {"link": "https://dentalperezyance.com/", "text": "Dental Pérez Yance"}
                ],
            },
        ],
    }
    result = google_ai_mode.parse_response({"text_blocks": [card, dict(card)]})
    assert result.text.splitlines() == [
        "- Ubicación: Av. José Pardo 434, Miraflores.",
        "- Referencia: más detalles en Dental Pérez Yance.",
    ]
    assert [c.url for c in result.citations] == ["https://dentalperezyance.com/"]
