"""API prices read from data/tarifas.toml (never hard-coded)."""

import tomllib
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path

from visible_ia.motor.modelos import Usage

RATES_TOML = Path(__file__).resolve().parents[3] / "data" / "tarifas.toml"


@dataclass(frozen=True)
class ModelRate:
    input_per_mtok: float
    cached_input_per_mtok: float
    output_per_mtok: float
    checked_on: date


@dataclass(frozen=True)
class OpenAIRates:
    models: dict[str, ModelRate]
    web_search_per_call: float

    def model(self, name: str) -> ModelRate:
        try:
            return self.models[name]
        except KeyError:
            raise KeyError(f"No hay tarifa para el modelo {name} en {RATES_TOML.name}") from None

    def cost(self, model: str, usage: Usage, searches: int) -> float:
        rate = self.model(model)
        uncached = max(usage.input_tokens - usage.cached_input_tokens, 0)
        tokens = (
            uncached * rate.input_per_mtok
            + usage.cached_input_tokens * rate.cached_input_per_mtok
            + usage.output_tokens * rate.output_per_mtok
        ) / 1_000_000
        return round(searches * self.web_search_per_call + tokens, 6)


def load_openai_rates(path: Path = RATES_TOML) -> OpenAIRates:
    data = tomllib.loads(path.read_text(encoding="utf-8"))["openai"]
    models = {
        name: ModelRate(
            m["input_per_mtok"], m["cached_input_per_mtok"], m["output_per_mtok"], m["checked_on"]
        )
        for name, m in data["models"].items()
    }
    return OpenAIRates(models, data["web_search"]["per_call"])


@cache
def openai_rates() -> OpenAIRates:
    return load_openai_rates()
