import json
import os
from pathlib import Path
from types import SimpleNamespace

import httpx
import openai
import pytest

from visible_ia.motor import chatgpt_api
from visible_ia.motor.modelos import Usage
from visible_ia.motor.tarifas import load_openai_rates

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "openai_response.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_parse_extracts_text_citations_and_tokens():
    result = chatgpt_api.parse_response(load_fixture())

    assert result.surface == "chatgpt_api"
    assert result.provider == "openai"
    assert result.model == "gpt-5-mini-2025-08-07"
    assert result.text.startswith("Estas son algunas clínicas de implantes en Miraflores")
    assert "Implant Studio Lima" in result.text
    assert [c.url for c in result.citations] == [
        "https://www.sonrisaandina.pe/implantes?utm_source=openai",
        "https://www.doctoralia.pe/implantologia/lima",
    ]
    assert result.citations[1].title == "Implantólogos en Lima - Doctoralia"
    assert result.usage == Usage(
        input_tokens=12000, cached_input_tokens=2000, output_tokens=1500, reasoning_tokens=1024
    )
    assert result.searches == 2  # the open_page action is not billed
    assert not result.empty
    assert result.raw["id"] == "resp_fixture_0001"


def test_cost_is_searches_plus_tokens_at_table_rates():
    result = chatgpt_api.parse_response(load_fixture())
    # 2 × 0.01 + (10000 × 0.25 + 2000 × 0.025 + 1500 × 2.00) / 1e6
    assert result.cost_usd == pytest.approx(0.02 + 0.00555)


def test_rates_come_from_the_dated_table():
    rates = load_openai_rates()
    assert rates.web_search_per_call == 0.01
    assert rates.model("gpt-5-mini").checked_on.isoformat() == "2026-09-26"
    with pytest.raises(KeyError):
        rates.model("gpt-unknown")


def test_real_answer_parses():
    """Recorded on 2026-09-26 from the verification call (C3-T01): cost US$0.028."""
    raw = json.loads(FIXTURE.with_name("openai_response_real.json").read_text(encoding="utf-8"))
    result = chatgpt_api.parse_response(raw)
    assert result.searches == 2
    assert len(result.citations) == 7  # 9 annotations, two URLs repeated
    assert raw["tool_usage"]["web_search"]["num_requests"] == 2
    raw["tool_usage"]["web_search"]["num_requests"] = 5  # the billed count wins
    assert chatgpt_api.parse_response(raw).searches == 5
    assert result.usage.input_tokens == 13290 and result.usage.output_tokens == 2339
    assert result.cost_usd == pytest.approx(0.028, abs=0.0005)


def test_answer_without_text_is_marked_empty():
    raw = {"model": "gpt-5-mini", "output": [], "usage": {}}
    result = chatgpt_api.parse_response(raw)
    assert result.empty and result.text == "" and result.cost_usd == 0


def _status_error(status: int) -> openai.APIStatusError:
    request = httpx.Request("POST", "https://api.openai.com/v1/responses")
    response = httpx.Response(status, request=request)
    cls = {429: openai.RateLimitError, 400: openai.BadRequestError}.get(
        status, openai.InternalServerError
    )
    return cls("boom", response=response, body=None)


class FakeClient:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return SimpleNamespace(model_dump=lambda mode: outcome)


def test_request_uses_web_search_located_in_lima():
    client = FakeClient([load_fixture()])
    chatgpt_api.ask("¿Dónde me pongo implantes en Miraflores?", client=client)

    call = client.calls[0]
    assert call["model"] == "gpt-5-mini"
    assert call["input"] == "¿Dónde me pongo implantes en Miraflores?"
    assert call["tools"] == [
        {
            "type": "web_search",
            "user_location": {
                "type": "approximate",
                "country": "PE",
                "city": "Lima",
                "region": "Lima",
                "timezone": "America/Lima",
            },
        }
    ]


def test_429_and_5xx_are_retried_with_growing_waits():
    waits = []
    client = FakeClient(
        [_status_error(429), _status_error(503), _status_error(500), load_fixture()]
    )
    result = chatgpt_api.ask("q", client=client, sleep=waits.append)
    assert result.text
    assert len(client.calls) == 4
    assert waits == [2, 4, 8]


def test_gives_up_after_three_retries():
    waits = []
    client = FakeClient([_status_error(429)] * 4)
    with pytest.raises(openai.RateLimitError):
        chatgpt_api.ask("q", client=client, sleep=waits.append)
    assert len(client.calls) == 4
    assert waits == [2, 4, 8]


def test_other_errors_propagate_without_retry():
    waits = []
    client = FakeClient([_status_error(400)])
    with pytest.raises(openai.BadRequestError):
        chatgpt_api.ask("q", client=client, sleep=waits.append)
    assert len(client.calls) == 1 and waits == []


@pytest.mark.live
def test_live_single_call():
    """One real call (≈ US$0.01–0.04). Run with: uv run pytest -m live -k chatgpt -s"""
    from visible_ia.config import get_settings

    key = get_settings().openai_api_key
    if key is None:
        pytest.skip("Falta OPENAI_API_KEY")
    result = chatgpt_api.ask(
        "¿Qué clínica me recomiendas para implantes dentales en Miraflores?",
        api_key=key.get_secret_value(),
    )
    if os.environ.get("SAVE_LIVE_FIXTURE"):
        out = FIXTURE.with_name("openai_response_live.json")
        out.write_text(json.dumps(result.raw, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nbúsquedas={result.searches} uso={result.usage} costo=US${result.cost_usd:.4f}")
    print(result.text[:500])
    assert result.text and result.searches >= 1
