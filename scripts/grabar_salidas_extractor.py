"""Record the extractor's raw candidates for every answer of the evaluation set (C4-T05).

Runs gpt-5-nano once per answer of data/eval/extractor-gold.jsonl (63 answers, ≈ US$0.007)
and writes data/eval/extractor-salidas.jsonl, which the CI quality test replays at no cost.
Re-run it only when extractor/prompt.md changes, with the Director's OK (it costs money).

    uv run python scripts/grabar_salidas_extractor.py [--incluir-propuestas]
"""

import json
import sys

import openai

from visible_ia.config import get_settings
from visible_ia.extractor import evaluacion, llm


def main() -> None:
    key = get_settings().openai_api_key
    if key is None:
        sys.exit("Falta OPENAI_API_KEY en .env")
    client = openai.OpenAI(api_key=key.get_secret_value(), max_retries=0, timeout=llm.TIMEOUT_SECONDS)
    prompt = llm.load_prompt()
    gold = evaluacion.read_jsonl(evaluacion.GOLD)
    total = 0.0
    rows = []
    for item in gold:
        result = llm.extract(
            item["texto"], link_texts=item.get("enlaces"), client=client, prompt=prompt
        )
        output = llm._output_text(result.raw) if result.raw else '{"menciones": []}'
        rows.append(
            {
                "id": item["id"],
                "extractor_version": prompt.extractor_version,
                "candidatos": json.loads(output or '{"menciones": []}').get("menciones") or [],
                "costo_usd": result.cost_usd,
            }
        )
        total += result.cost_usd
        print(f"  {item['id']}: {[m.raw_name for m in result.mentions]}")
    with evaluacion.OUTPUTS.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    scores = evaluacion.score(gold, {r["id"]: r["candidatos"] for r in rows}, include_proposed=True)
    print(f"\nGrabadas {len(rows)} salidas en {evaluacion.OUTPUTS.name} · costo US${total:.4f}")
    print("Con las etiquetas propuestas (aún sin confirmar): " + scores.report())


if __name__ == "__main__":
    main()
