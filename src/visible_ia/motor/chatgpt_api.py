"""ChatGPT through the official API: Responses API + web_search tool, located in Lima (ADR-002).

Only the API is used; the consumer app is never automated or scraped.
"""

import time
from collections.abc import Callable
from typing import Any

import openai

from visible_ia.motor.modelos import Citation, EngineResponse, Usage
from visible_ia.motor.tarifas import OpenAIRates, openai_rates

MODEL = "gpt-5-mini"
USER_LOCATION = {
    "type": "approximate",
    "country": "PE",
    "city": "Lima",
    "region": "Lima",
    "timezone": "America/Lima",
}
MAX_RETRIES = 3
BACKOFF_SECONDS = (2, 4, 8)
TIMEOUT_SECONDS = 180


def _is_retryable(exc: Exception) -> bool:
    return isinstance(exc, openai.APIStatusError) and (
        exc.status_code == 429 or exc.status_code >= 500
    )


def ask(
    question: str,
    *,
    client: openai.OpenAI | None = None,
    api_key: str | None = None,
    model: str = MODEL,
    rates: OpenAIRates | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> EngineResponse:
    """Ask one question with web search and return the parsed answer."""
    # The SDK's own retries are disabled so the policy lives here (429 and 5xx, 3 times).
    client = client or openai.OpenAI(api_key=api_key, max_retries=0, timeout=TIMEOUT_SECONDS)
    response = with_retries(
        lambda: client.responses.create(
            model=model,
            input=question,
            tools=[{"type": "web_search", "user_location": USER_LOCATION}],
        ),
        sleep=sleep,
    )
    return parse_response(response.model_dump(mode="json"), rates=rates)


def with_retries[T](call: Callable[[], T], *, sleep: Callable[[float], None] = time.sleep) -> T:
    """Run an OpenAI call, retrying 429 and 5xx up to 3 times (2, 4, 8 s); the rest propagates."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            return call()
        except Exception as exc:
            if attempt == MAX_RETRIES or not _is_retryable(exc):
                raise
            sleep(BACKOFF_SECONDS[attempt])
    raise AssertionError("unreachable")


def parse_response(raw: dict[str, Any], *, rates: OpenAIRates | None = None) -> EngineResponse:
    """Build an EngineResponse from a Responses API payload (as JSON)."""
    texts: list[str] = []
    citations: list[Citation] = []
    seen: set[str] = set()
    searches = 0
    for item in raw.get("output") or []:
        kind = item.get("type")
        if kind == "web_search_call":
            action = item.get("action") or {}
            # Only "search" actions are billed; open_page / find_in_page are not.
            if action.get("type", "search") == "search":
                searches += 1
        elif kind == "message":
            for part in item.get("content") or []:
                if part.get("type") != "output_text":
                    continue
                texts.append(part.get("text") or "")
                for ann in part.get("annotations") or []:
                    url = ann.get("url")
                    if ann.get("type") == "url_citation" and url and url not in seen:
                        seen.add(url)
                        citations.append(Citation(url=url, title=ann.get("title")))

    usage_raw = raw.get("usage") or {}
    usage = Usage(
        input_tokens=usage_raw.get("input_tokens") or 0,
        cached_input_tokens=(usage_raw.get("input_tokens_details") or {}).get("cached_tokens") or 0,
        output_tokens=usage_raw.get("output_tokens") or 0,
        reasoning_tokens=(usage_raw.get("output_tokens_details") or {}).get("reasoning_tokens")
        or 0,
    )
    # The billed count, when the API reports it, wins over counting the output items.
    billed = ((raw.get("tool_usage") or {}).get("web_search") or {}).get("num_requests")
    if billed is not None:
        searches = billed
    model = raw.get("model") or MODEL
    rates = rates or openai_rates()
    text = "\n\n".join(t for t in texts if t).strip()
    return EngineResponse(
        surface="chatgpt_api",
        provider="openai",
        model=model,
        text=text,
        citations=citations,
        searches=searches,
        usage=usage,
        cost_usd=rates.cost(_rate_key(model, rates), usage, searches),
        empty=not text,
        raw=raw,
    )


def _rate_key(model: str, rates: OpenAIRates) -> str:
    # The API returns dated snapshots such as "gpt-5-mini-2025-08-07".
    if model in rates.models:
        return model
    matches = [name for name in rates.models if model.startswith(f"{name}-")]
    return max(matches, key=len) if matches else model
