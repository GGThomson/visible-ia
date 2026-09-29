"""Vocabulary of the niche (C-010): the words new code uses for the business and its customers."""

import tomllib
from dataclasses import dataclass
from pathlib import Path

NICHE_TOML = Path(__file__).resolve().parent / "nicho.toml"


@dataclass(frozen=True)
class Niche:
    business: str  # "clínica"
    businesses: str  # "clínicas"
    customer: str  # "paciente"
    customers: str  # "pacientes"
    customer_article: str  # "un" ("como lo haría un paciente")
    categories: dict[str, str]  # category code -> what the customer looks for

    def category(self, code: str) -> str:
        return self.categories.get(code, code)


def load_niche(path: Path = NICHE_TOML) -> Niche:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return Niche(
        business=data["negocio"]["singular"],
        businesses=data["negocio"]["plural"],
        customer=data["cliente_final"]["singular"],
        customers=data["cliente_final"]["plural"],
        customer_article=data["cliente_final"]["articulo"],
        categories=dict(data["categorias"]),
    )
