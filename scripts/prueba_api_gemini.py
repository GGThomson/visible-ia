"""Gemini API source test: same 10 sample questions, grounded with Google Search (+ Maps).

Proposal: docs/01-descubrimiento/prueba-fuentes/propuesta-api-gemini.md
Reads GEMINI_API_KEY from .env (never printed). Free tier only: stops on quota errors.

Usage:
    python scripts/prueba_api_gemini.py --dry-run
    python scripts/prueba_api_gemini.py --configs A B --reps 3
    python scripts/prueba_api_gemini.py --configs B-en --reps 3
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "docs" / "01-descubrimiento" / "prueba-fuentes"
OUT_CSV = OUT_DIR / "registro-api.csv"
OUT_RAW = OUT_DIR / "registro-api-crudo.jsonl"

# Free tier: grounding (Search/Maps) is only available on 2.5 models, not on 3.x.
DEFAULT_MODEL = "gemini-2.5-flash"
MIRAFLORES = (-12.1211, -77.0297)
PAUSE_SECONDS = 7  # stay under free-tier requests-per-minute

QUESTIONS = {
    "Q01": ("¿Cuál es la mejor clínica de implantes dentales en Miraflores?",
            "What is the best dental implant clinic in Miraflores, Lima?"),
    "Q05": ("¿Cuáles son las clínicas dentales más confiables en Lima para implantes?",
            "Which are the most trustworthy dental clinics in Lima for implants?"),
    "Q10": ("¿Dónde me hago carillas dentales en San Isidro?",
            "Where can I get dental veneers in San Isidro, Lima?"),
    "Q11": ("Recomiéndame un lugar para ortodoncia invisible (Invisalign) en Surco",
            "Recommend me a place for invisible orthodontics (Invisalign) in Surco, Lima"),
    "Q16": ("¿Cuál es la mejor clínica estética en Miraflores?",
            "What is the best aesthetic clinic in Miraflores, Lima?"),
    "Q19": ("¿Qué clínicas de medicina estética en Lima son seguras y tienen buenas reseñas?",
            "Which aesthetic medicine clinics in Lima are safe and have good reviews?"),
    "Q22": ("¿Qué clínica estética en Surco tiene buenos precios?",
            "Which aesthetic clinic in Surco, Lima has good prices?"),
    "Q24": ("¿Cuál es el mejor dermatólogo en Miraflores?",
            "Who is the best dermatologist in Miraflores, Lima?"),
    "Q29": ("¿Cuál es la clínica dermatológica mejor valorada en San Isidro?",
            "What is the best-rated dermatology clinic in San Isidro, Lima?"),
    "Q30": ("Necesito un dermatólogo para caída de cabello en Surco, ¿a quién voy?",
            "I need a dermatologist for hair loss in Surco, Lima. Who should I see?"),
}

MAPS_TOOL = {"type": "google_maps", "latitude": MIRAFLORES[0], "longitude": MIRAFLORES[1]}
CONFIGS = {
    "A": {"tools": [{"type": "google_search"}], "english": False},
    "B": {"tools": [{"type": "google_search"}, MAPS_TOOL], "english": False},
    "B-en": {"tools": [{"type": "google_search"}, MAPS_TOOL], "english": True},
}

FIELDS = ["fecha", "ia", "pregunta_id", "repeticion", "modo", "busco_web", "respuesta",
          "fuentes_citadas", "notas", "modelo", "config", "consultas_busqueda", "lugares_maps"]


class QuotaExhausted(Exception):
    pass


def load_key():
    try:
        from dotenv import load_dotenv
    except ImportError:
        sys.exit("Falta python-dotenv: python -m pip install python-dotenv")
    load_dotenv(ROOT / ".env")
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        sys.exit("No hay GEMINI_API_KEY en .env (raíz del proyecto).")
    return key


def build_input(qid, english):
    es, en = QUESTIONS[qid]
    return f"{en} Please answer in Spanish." if english else es


def parse(interaction):
    """Return (text, url sources, maps places, search queries) from an interaction."""
    texts, urls, places, queries = [], [], [], []
    for step in interaction.steps or []:
        if step.type in ("google_search_call", "google_maps_call"):
            queries.extend(getattr(step, "queries", None) or [])
        if step.type != "model_output":
            continue
        for block in step.content or []:
            if block.type != "text":
                continue
            texts.append(block.text)
            for ann in block.annotations or []:
                if ann.type == "url_citation" and ann.url not in urls:
                    urls.append(ann.url)
                elif ann.type == "place_citation" and ann.name not in places:
                    places.append(ann.name)
    return "\n".join(texts), urls, places, queries


def call(client, model, cfg, text, retries=3):
    for attempt in range(retries):
        try:
            return client.interactions.create(model=model, input=text, tools=cfg["tools"])
        except Exception as exc:  # SDK raises APIError subclasses; keep message only
            msg = str(exc)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                if "per day" in msg.lower() or "perday" in msg.lower():
                    raise QuotaExhausted(msg[:300])
                time.sleep(30 * (attempt + 1))
                continue
            raise
    raise QuotaExhausted("Rate limit persistente tras reintentos")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", nargs="+", default=["A", "B"], choices=list(CONFIGS))
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--questions", nargs="+", default=list(QUESTIONS))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    done = set()
    if OUT_CSV.exists():  # resume: skip calls already answered (free tier allows ~20/day per model)
        with open(OUT_CSV, encoding="utf-8", newline="") as f:
            done = {(r["config"], r["pregunta_id"], int(r["repeticion"]))
                    for r in csv.DictReader(f) if not r["notas"].startswith("ERROR")}
    plan = [(c, q, r) for c in args.configs for q in args.questions for r in range(1, args.reps + 1)
            if (c, q, r) not in done]
    print(f"Plan: {len(plan)} llamadas · modelo {args.model} · configs {args.configs}")
    if args.dry_run:
        for c, q, r in plan[:3]:
            print(" ", c, q, r, "→", build_input(q, CONFIGS[c]["english"]))
        return

    from google import genai
    client = genai.Client(api_key=load_key())

    new_file = not OUT_CSV.exists()
    with open(OUT_CSV, "a", encoding="utf-8", newline="") as fcsv, \
            open(OUT_RAW, "a", encoding="utf-8") as fraw:
        writer = csv.DictWriter(fcsv, fieldnames=FIELDS, lineterminator="\r\n")
        if new_file:
            writer.writeheader()
        for i, (c, q, r) in enumerate(plan, 1):
            cfg = CONFIGS[c]
            try:
                inter = call(client, args.model, cfg, build_input(q, cfg["english"]))
                text, urls, places, queries = parse(inter)
                note = ""
                raw = inter.model_dump(mode="json", exclude_none=True)
            except QuotaExhausted as exc:
                print(f"Cuota gratuita agotada: me detengo. {exc}")
                break
            except Exception as exc:
                text, urls, places, queries, raw = "", [], [], [], None
                note = f"ERROR: {str(exc)[:300]}"
            writer.writerow({
                "fecha": dt.date.today().isoformat(), "ia": "gemini-api", "pregunta_id": q,
                "repeticion": r, "modo": "api", "busco_web": "si" if (queries or urls or places) else "no",
                "respuesta": text, "fuentes_citadas": "; ".join(urls) or "sin fuentes visibles",
                "notas": note, "modelo": args.model, "config": c,
                "consultas_busqueda": "; ".join(queries), "lugares_maps": "; ".join(places),
            })
            fcsv.flush()
            fraw.write(json.dumps({"config": c, "pregunta_id": q, "repeticion": r, "raw": raw},
                                  ensure_ascii=False) + "\n")
            print(f"[{i}/{len(plan)}] {c} {q} r{r}: {len(text)} chars, {len(urls)} urls, "
                  f"{len(places)} lugares {note[:120]}")
            time.sleep(PAUSE_SECONDS)


if __name__ == "__main__":
    main()
