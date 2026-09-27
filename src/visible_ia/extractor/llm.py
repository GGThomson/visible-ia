"""Mentions of clinics and professionals in an answer, in order, with gpt-5-nano (HU-07).

The model returns structured output (strict JSON Schema). Its list is never trusted as is:
names that do not appear literally in the answer (or in its link texts) are discarded, known
platforms are dropped, and the order comes from where each name first appears in the text.
"""

import json
import re
import time
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import openai

from visible_ia.motor.chatgpt_api import TIMEOUT_SECONDS, with_retries
from visible_ia.motor.modelos import Usage
from visible_ia.motor.tarifas import OpenAIRates, openai_rates

MODEL = "gpt-5-nano"
PROMPT_PATH = Path(__file__).with_name("prompt.md")
# Names that are never a clinic, even if the model says so (compared normalized).
PLATFORMS = frozenset(
    {
        "doctoralia",
        "doctoralia peru",
        "google",
        "google maps",
        "maps",
        "instagram",
        "facebook",
        "tiktok",
        "whatsapp",
        "youtube",
        "fresha",
        "waze",
        "lima dental rating",
        "colegio odontologico del peru",
    }
)
SCHEMA = {
    "type": "object",
    "properties": {
        "menciones": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nombre_tal_cual": {
                        "type": "string",
                        "description": "Solo el nombre, copiado del texto, sin sede ni descripción",
                    },
                    "orden": {"type": "integer", "description": "1, 2, 3… por primera aparición"},
                    "es_establecimiento_o_profesional": {
                        "type": "boolean",
                        "description": "true si atiende pacientes (clínica, centro o profesional); "
                        "false si es plataforma, directorio, marca, técnica o lugar",
                    },
                },
                "required": ["nombre_tal_cual", "orden", "es_establecimiento_o_profesional"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["menciones"],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class Prompt:
    version: str
    text: str

    @property
    def extractor_version(self) -> str:
        return f"{MODEL}/prompt-v{self.version}"


@dataclass(frozen=True)
class Mention:
    raw_name: str
    position: int


@dataclass
class Extraction:
    mentions: list[Mention]
    discarded: list[str] = field(default_factory=list)  # not literal, or not a clinic
    usage: Usage = field(default_factory=Usage)
    cost_usd: float = 0.0
    extractor_version: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


def load_prompt(path: Path = PROMPT_PATH) -> Prompt:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"<!--\s*version:\s*(\S+)\s*-->\s*", text)
    if not match:
        raise ValueError(f"{path.name} debe empezar con <!-- version: N -->")
    return Prompt(match.group(1), text[match.end() :].strip())


def normalize(text: str) -> str:
    """Lowercase, no accents, punctuation as spaces, single spaces."""
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^\w]+", " ", text).split())


def build_input(text: str, link_texts: list[str] | None = None) -> str:
    parts = [f"Respuesta:\n{text.strip()}"]
    if link_texts:
        parts.append("Textos de enlaces:\n" + "\n".join(f"- {t}" for t in link_texts))
    return "\n\n".join(parts)


def link_texts_from_raw(surface: str, raw: dict[str, Any]) -> list[str]:
    """Link texts of a Google AI Mode answer, where clinic cards keep their names."""
    if not surface.startswith("google_ai_mode"):
        return []
    from visible_ia.motor.google_ai_mode import snippet_links

    seen: list[str] = []
    for link in snippet_links(raw.get("text_blocks") or []):
        name = (link.get("text") or "").strip()
        if name and name not in seen:
            seen.append(name)
    return seen


def validate(
    candidates: list[dict[str, Any]], text: str, link_texts: list[str] | None = None
) -> tuple[list[Mention], list[str]]:
    """Keep literal, non-platform names, once each, ordered by first appearance."""
    haystack = f" {normalize(text)} "
    links = [f" {normalize(t)} " for t in link_texts or []]
    kept: list[tuple[int, int, str]] = []
    discarded: list[str] = []
    seen: set[str] = set()
    for cand in sorted(candidates, key=lambda c: c.get("orden") or 0):
        name = (cand.get("nombre_tal_cual") or "").strip()
        key = normalize(name)
        if not key or key in seen:
            continue
        if not cand.get("es_establecimiento_o_profesional") or key in PLATFORMS:
            discarded.append(name)
            continue
        where = haystack.find(f" {key} ")
        in_links = any(f" {key} " in link for link in links)
        if where < 0 and not in_links:
            discarded.append(name)
            continue
        seen.add(key)
        # Names found only in link texts keep the model's order, after the ones in the text.
        kept.append((where if where >= 0 else len(haystack), len(kept), name))
    kept.sort()
    return [Mention(name, i) for i, (_, _, name) in enumerate(kept, start=1)], discarded


def extract(
    text: str,
    *,
    link_texts: list[str] | None = None,
    client: openai.OpenAI | None = None,
    api_key: str | None = None,
    prompt: Prompt | None = None,
    rates: OpenAIRates | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> Extraction:
    """Extract the mentions of one answer (one gpt-5-nano call, ≈ US$0.0002)."""
    prompt = prompt or load_prompt()
    if not text.strip():
        return Extraction(mentions=[], extractor_version=prompt.extractor_version)
    client = client or openai.OpenAI(api_key=api_key, max_retries=0, timeout=TIMEOUT_SECONDS)
    response = with_retries(
        lambda: client.responses.create(
            model=MODEL,
            instructions=prompt.text,
            input=build_input(text, link_texts),
            reasoning={"effort": "minimal"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": "menciones",
                    "schema": SCHEMA,
                    "strict": True,
                }
            },
        ),
        sleep=sleep,
    )
    raw = response.model_dump(mode="json")
    return parse_response(raw, text, link_texts, prompt=prompt, rates=rates)


def parse_response(
    raw: dict[str, Any],
    text: str,
    link_texts: list[str] | None = None,
    *,
    prompt: Prompt | None = None,
    rates: OpenAIRates | None = None,
) -> Extraction:
    prompt = prompt or load_prompt()
    output = _output_text(raw)
    if output is None:
        raise ValueError("El extractor no devolvió salida (¿rechazo del modelo?)")
    candidates = json.loads(output).get("menciones") or []
    mentions, discarded = validate(candidates, text, link_texts)
    usage_raw = raw.get("usage") or {}
    usage = Usage(
        input_tokens=usage_raw.get("input_tokens") or 0,
        cached_input_tokens=(usage_raw.get("input_tokens_details") or {}).get("cached_tokens") or 0,
        output_tokens=usage_raw.get("output_tokens") or 0,
        reasoning_tokens=(usage_raw.get("output_tokens_details") or {}).get("reasoning_tokens")
        or 0,
    )
    return Extraction(
        mentions=mentions,
        discarded=discarded,
        usage=usage,
        cost_usd=(rates or openai_rates()).cost(MODEL, usage, searches=0),
        extractor_version=prompt.extractor_version,
        raw=raw,
    )


def _output_text(raw: dict[str, Any]) -> str | None:
    for item in raw.get("output") or []:
        if item.get("type") != "message":
            continue
        for part in item.get("content") or []:
            if part.get("type") == "output_text":
                return part.get("text")
    return None
