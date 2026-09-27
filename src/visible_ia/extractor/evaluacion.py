"""Extractor quality against the hand-labelled set (PRD §5.3).

- Mentions: precision (what it marks is a clinic) and recall (it finds the ones there).
  A predicted name counts as a labelled one when both fold to the same text, one contains
  the other as whole words ("Dr. Aldo" / "Dr. Aldo | Implantes Dentales…"), or `match`
  associates them.
- Association (answers of a market with a clinic list): among the labelled mentions the
  extractor found, the share matched to the labelled clinic. Mentions it missed are already
  counted by recall and are not counted twice.
- Domains: the source domains computed from the cited URLs.

Only answers the Director confirmed count, unless `include_proposed` is set.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from visible_ia.extractor import llm
from visible_ia.extractor.matching import ClinicCandidate, match
from visible_ia.mercados.alias import fold
from visible_ia.motor.corrida import domain_of

EVAL_DIR = Path(__file__).resolve().parents[3] / "data" / "eval"
GOLD = EVAL_DIR / "extractor-gold.jsonl"
OUTPUTS = EVAL_DIR / "extractor-salidas.jsonl"
CLINIC_LISTS = {"corrida1-": EVAL_DIR / "clinicas-IMP-Miraflores.json"}
TARGETS = {"precision": 0.95, "recall": 0.90, "association": 0.95, "domains": 0.95}


@dataclass
class Scores:
    answers: int = 0
    predicted: int = 0
    labelled: int = 0
    true_positives: int = 0
    found: int = 0
    association_total: int = 0
    association_ok: int = 0
    domains_total: int = 0
    domains_ok: int = 0
    errors: list[str] = field(default_factory=list)

    @staticmethod
    def _ratio(num: int, den: int) -> float:
        return num / den if den else 1.0

    @property
    def precision(self) -> float:
        return self._ratio(self.true_positives, self.predicted)

    @property
    def recall(self) -> float:
        return self._ratio(self.found, self.labelled)

    @property
    def association(self) -> float:
        return self._ratio(self.association_ok, self.association_total)

    @property
    def domains(self) -> float:
        return self._ratio(self.domains_ok, self.domains_total)

    def failing(self) -> dict[str, float]:
        values = {name: getattr(self, name) for name in TARGETS}
        return {name: v for name, v in values.items() if v < TARGETS[name]}

    def report(self) -> str:
        return (
            f"{self.answers} respuestas · precisión {self.precision:.1%} "
            f"({self.true_positives}/{self.predicted}) · exhaustividad {self.recall:.1%} "
            f"({self.found}/{self.labelled}) · asociación {self.association:.1%} "
            f"({self.association_ok}/{self.association_total}) · dominios {self.domains:.1%}"
        )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_clinic_list(path: Path) -> list[ClinicCandidate]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        ClinicCandidate(i, c["nombre"], tuple(c.get("alias") or ()))
        for i, c in enumerate(data["clinicas"], start=1)
    ]


def _words(text: str) -> str:
    return f" {fold(text)} "


def best_hit(names: list[str], labelled: str) -> str | None:
    """The extracted name that corresponds to a label: identical first, then contained, then
    matched (so "Smiles Perú" is not taken for the label "Digital Smiles")."""
    target = fold(labelled)
    for test in (
        lambda n: fold(n) == target,
        lambda n: _words(n) in _words(labelled) or _words(labelled) in _words(n),
        lambda n: same_name(n, labelled),
    ):
        hit = next((n for n in names if test(n)), None)
        if hit:
            return hit
    return None


def same_name(predicted: str, labelled: str) -> bool:
    a, b = _words(predicted), _words(labelled)
    if a.strip() == b.strip() or a in b or b in a:
        return True
    return match(predicted, [ClinicCandidate(1, labelled)]).status == "matched"


def score(
    gold: list[dict[str, Any]],
    outputs: dict[str, list[dict[str, Any]]],
    *,
    include_proposed: bool = False,
) -> Scores:
    """`outputs` maps answer id -> the model's candidate list (before validation)."""
    scores = Scores()
    clinic_lists = {prefix: load_clinic_list(path) for prefix, path in CLINIC_LISTS.items()}
    for item in gold:
        if item.get("estado") != "confirmada" and not include_proposed:
            continue
        if item["id"] not in outputs:
            scores.errors.append(f"sin salida grabada: {item['id']}")
            continue
        scores.answers += 1
        predicted, _ = llm.validate(outputs[item["id"]], item["texto"], item.get("enlaces"))
        names = [m.raw_name for m in predicted]
        labelled = item["menciones"]
        scores.predicted += len(names)
        scores.labelled += len(labelled)
        scores.true_positives += sum(
            any(same_name(n, g["nombre"]) for g in labelled) for n in names
        )
        scores.found += sum(any(same_name(n, g["nombre"]) for n in names) for g in labelled)

        clinics = next((c for p, c in clinic_lists.items() if item["id"].startswith(p)), None)
        if clinics:
            by_id = {c.id: c.name for c in clinics}
            for g in labelled:
                hit = best_hit(names, g["nombre"]) if g.get("clinica") else None
                if hit is None:
                    continue
                scores.association_total += 1
                result = match(hit, clinics)
                if result.status == "matched" and by_id[result.clinic_id] == g["clinica"]:
                    scores.association_ok += 1

        expected = set(item.get("dominios") or [])
        got = {d for d in (domain_of(u) for u in item.get("fuentes") or []) if d}
        scores.domains_total += len(expected)
        scores.domains_ok += len(expected & got)
    return scores


def load_outputs(path: Path = OUTPUTS) -> dict[str, list[dict[str, Any]]]:
    return {row["id"]: row["candidatos"] for row in read_jsonl(path)} if path.exists() else {}
