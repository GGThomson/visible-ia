"""Google AI Mode through SerpApi (ADR-002), located in Lima and in Spanish.

httpx is used directly (no SerpApi SDK) to keep control of the retries. Every repetition
must be a fresh answer, so SerpApi's 1-hour cache is disabled (no_cache=true).
"""

import time
from collections.abc import Callable
from typing import Any

import httpx

from visible_ia.motor.modelos import Citation, EngineResponse

ENDPOINT = "https://serpapi.com/search.json"
PARAMS = {"engine": "google_ai_mode", "location": "Lima, Peru", "hl": "es", "gl": "pe"}
MAX_RETRIES = 3
BACKOFF_SECONDS = (2, 4, 8)
TIMEOUT_SECONDS = 120
# SerpApi answers HTTP 200 with an "error" field when Google shows no AI answer.
NO_ANSWER_MARKERS = ("hasn't returned any results",)


class SerpApiError(RuntimeError):
    pass


def ask(
    question: str,
    *,
    api_key: str,
    client: httpx.Client | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> EngineResponse:
    """Ask one question to Google AI Mode and return the parsed answer (1 SerpApi credit)."""
    params = {**PARAMS, "q": question, "no_cache": "true", "api_key": api_key}
    own_client = client is None
    client = client or httpx.Client(timeout=TIMEOUT_SECONDS)
    try:
        for attempt in range(MAX_RETRIES + 1):
            response = client.get(ENDPOINT, params=params)
            retryable = response.status_code == 429 or response.status_code >= 500
            if not retryable or attempt == MAX_RETRIES:
                break
            sleep(BACKOFF_SECONDS[attempt])
    finally:
        if own_client:
            client.close()
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    if response.status_code != 200:
        message = payload.get("error") or response.text[:200]
        raise SerpApiError(f"SerpApi respondió {response.status_code}: {message}")
    return parse_response(payload)


def parse_response(raw: dict[str, Any]) -> EngineResponse:
    """Build an EngineResponse from a SerpApi google_ai_mode payload."""
    error = raw.get("error")
    if error and not _is_no_answer(error):
        raise SerpApiError(f"SerpApi: {error}")
    text = (raw.get("reconstructed_markdown") or "").strip() or blocks_to_text(
        raw.get("text_blocks") or []
    )
    citations: list[Citation] = []
    seen: set[str] = set()
    for ref in raw.get("references") or []:
        url = ref.get("link")
        if url and url not in seen:
            seen.add(url)
            citations.append(Citation(url=url, title=ref.get("title")))
    return EngineResponse(
        surface="google_ai_mode",
        provider="serpapi",
        model="google_ai_mode",
        text=text,
        citations=citations,
        searches=1,
        cost_usd=0.0,  # free plan: the limit is the monthly credit quota, not money
        empty=not text,
        raw=_without_secrets(raw),
    )


def blocks_to_text(blocks: list[dict[str, Any]]) -> str:
    """Rebuild readable text from text_blocks, keeping the order in which clinics appear."""
    return "\n".join(_block_lines(blocks, depth=0)).strip()


def _block_lines(blocks: list[dict[str, Any]], depth: int) -> list[str]:
    lines: list[str] = []
    indent = "  " * depth
    for block in blocks:
        kind = block.get("type")
        snippet = (block.get("snippet") or "").strip()
        title = (block.get("title") or "").strip()
        if kind == "heading" and snippet:
            lines.append(f"{indent}## {snippet}")
        elif kind == "list" or "list" in block:
            if snippet:
                lines.append(f"{indent}{snippet}")
            for item in block.get("list") or []:
                head = " ".join(p for p in (item.get("title"), item.get("snippet")) if p).strip()
                if head:
                    lines.append(f"{indent}- {head}")
                if item.get("list"):
                    lines.extend(_block_lines([{"list": item["list"]}], depth + 1))
        elif snippet or title:
            lines.append(indent + " ".join(p for p in (title, snippet) if p))
    return lines


def _is_no_answer(error: str) -> bool:
    lowered = error.lower()
    return any(marker in lowered for marker in NO_ANSWER_MARKERS)


def _without_secrets(raw: dict[str, Any]) -> dict[str, Any]:
    # search_parameters never carries the key, but the metadata URLs might: drop them.
    clean = dict(raw)
    metadata = dict(clean.get("search_metadata") or {})
    for key in ("json_endpoint", "raw_html_file", "prettify_html_file"):
        metadata.pop(key, None)
    if metadata:
        clean["search_metadata"] = metadata
    return clean
