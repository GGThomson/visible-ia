"""Google AI Mode through SerpApi (ADR-002), located in Lima and in Spanish.

httpx is used directly (no SerpApi SDK) to keep control of the retries. Every repetition
must be a fresh answer, so SerpApi's 1-hour cache is disabled (no_cache=true).
"""

import re
import time
from collections.abc import Callable
from typing import Any

import httpx

from visible_ia.motor.modelos import Citation, EngineResponse

ENDPOINT = "https://serpapi.com/search.json"
ACCOUNT_ENDPOINT = "https://serpapi.com/account.json"
PARAMS = {"engine": "google_ai_mode", "location": "Lima, Peru", "hl": "es", "gl": "pe"}
MAX_RETRIES = 3
BACKOFF_SECONDS = (2, 4, 8)
TIMEOUT_SECONDS = 120
# SerpApi answers HTTP 200 with an "error" field when Google shows no AI answer.
NO_ANSWER_MARKERS = ("hasn't returned any results",)
# Google sometimes returns HTTP 200 with a rate-limit notice as the AI answer (run 1, 26/09).
RATE_LIMIT_MARKERS = (
    "alcanzaste el límite de solicitudes de respuestas de ia",
    "you've reached the limit",
)
# Concurrent AI Mode searches trigger that limit: one at a time (the plan allows up to 3).
MAX_CONCURRENCY = 1
# Place cards leak their button labels into the snippet ("LlamarCómo llegarSitio web...").
CARD_BUTTONS = re.compile(r"^(?:Llamar|Cómo llegar|Sitio web|Call|Directions|Website)+\s*")
MARKDOWN_REFERENCES = re.compile(r"\n#+\s*References\s*\n.*\Z", re.DOTALL)


class SerpApiError(RuntimeError):
    pass


class GoogleRateLimited(SerpApiError):
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


def account_usage(api_key: str, *, client: httpx.Client | None = None) -> int:
    """Searches used this month according to the SerpApi account (free: no credit)."""
    own_client = client is None
    client = client or httpx.Client(timeout=30)
    try:
        response = client.get(ACCOUNT_ENDPOINT, params={"api_key": api_key})
    finally:
        if own_client:
            client.close()
    if response.status_code != 200:
        raise SerpApiError(f"SerpApi (cuenta) respondió {response.status_code}")
    return int(response.json().get("this_month_usage") or 0)


def parse_response(raw: dict[str, Any]) -> EngineResponse:
    """Build an EngineResponse from a SerpApi google_ai_mode payload."""
    error = raw.get("error")
    if error and not _is_no_answer(error):
        raise SerpApiError(f"SerpApi: {error}")
    blocks = raw.get("text_blocks") or []
    # text_blocks first: reconstructed_markdown escapes characters and appends the references.
    text = (
        blocks_to_text(blocks)
        or MARKDOWN_REFERENCES.sub("", raw.get("reconstructed_markdown") or "").strip()
    )
    if any(marker in text.lower() for marker in RATE_LIMIT_MARKERS):
        # Google answered with its own limit message: not an answer, the call must be redone.
        raise GoogleRateLimited(f"Google limitó las respuestas de IA: {text[:120]}")
    citations: list[Citation] = []
    seen: set[str] = set()
    # Inline links carry the clinics' real websites; references are often Google viewer URLs.
    links = [(x.get("link"), x.get("text")) for x in snippet_links(blocks)]
    links += [(r.get("link"), r.get("title")) for r in raw.get("references") or []]
    for url, title in links:
        if url and url not in seen:
            seen.add(url)
            citations.append(Citation(url=url, title=title))
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
    previous = None
    for block in blocks:
        # Place cards come twice in a row, identical: keep one.
        if block == previous:
            continue
        previous = block
        kind = block.get("type")
        snippet = CARD_BUTTONS.sub("", (block.get("snippet") or "").strip())
        title = (block.get("title") or "").strip()
        if kind == "heading" and snippet:
            lines.append(f"{indent}## {snippet}")
        elif kind == "list" or "list" in block:
            if snippet:
                lines.append(f"{indent}{snippet}")
            for item in block.get("list") or []:
                item_snippet = CARD_BUTTONS.sub("", (item.get("snippet") or "").strip())
                head = " ".join(p for p in (item.get("title"), item_snippet) if p).strip()
                if head:
                    lines.append(f"{indent}- {head}")
                if item.get("list"):
                    lines.extend(_block_lines([{"list": item["list"]}], depth + 1))
        elif snippet or title:
            lines.append(indent + " ".join(p for p in (title, snippet) if p))
    return lines


def snippet_links(blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    links: list[dict[str, Any]] = []
    for block in blocks:
        links.extend(block.get("snippet_links") or [])
        links.extend(snippet_links(block.get("list") or []))
    return links


def _is_no_answer(error: str) -> bool:
    lowered = error.lower()
    return any(marker in lowered for marker in NO_ANSWER_MARKERS)


def _without_secrets(raw: dict[str, Any]) -> dict[str, Any]:
    # search_parameters never carries the key; the metadata URLs are private links: drop them.
    clean = dict(raw)
    metadata = dict(clean.get("search_metadata") or {})
    for key in ("json_endpoint", "markdown_endpoint", "raw_html_file", "prettify_html_file"):
        metadata.pop(key, None)
    if metadata:
        clean["search_metadata"] = metadata
    return clean
