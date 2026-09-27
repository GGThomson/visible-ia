"""Clinic aliases (HU-03): one clinic must never count as two.

Google Maps names often pack several names and keywords ("Implantes Dental | Perez Yance /
Clínicas Dentales Americadent"). On import we split them into candidate aliases and drop the
generic ones: an automatic alias made only of category words ("Clínica Dental", "Implantes
Dentales", "Dermatología") would match every answer and inflate the index.
"""

import re
import unicodedata

import psycopg

# Generic vocabulary per category (singular/plural, with and without accents after folding).
GENERIC_BY_CATEGORY = {
    "IMP": {"implante", "implantes", "implantologia", "implantologo", "implantologa", "oral",
            "rehabilitacion", "protesis", "dental", "dentales", "dentista", "odontologia",
            "odontologico", "odontologos", "odontologo", "clinica", "clinicas", "centro",
            "consultorio", "especialistas", "especialista", "sonrisa"},
    "EDE": {"estetica", "dental", "dentales", "dentista", "carillas", "ortodoncia", "brackets",
            "alineadores", "invisibles", "invisible", "diseno", "sonrisa", "blanqueamiento",
            "clinica", "clinicas", "centro", "consultorio", "odontologia", "odontologico"},
    "MES": {"medicina", "estetica", "esteticas", "estetico", "clinica", "clinicas", "centro",
            "spa", "laser", "depilacion", "facial", "corporal", "antiaging", "belleza",
            "cirugia", "plastica", "medica", "medico"},
    "DER": {"dermatologia", "dermatologica", "dermatologico", "dermatologo", "dermatologa",
            "piel", "clinica", "clinicas", "centro", "consultorio", "laser", "tricologia",
            "capilar", "medico", "medica", "estetica"},
}  # fmt: skip
# Words that never make an alias specific on their own.
FILLER = {"mejor", "en", "de", "del", "la", "el", "los", "las", "y", "e", "sede", "lima",
          "miraflores", "san", "isidro", "surco", "santiago", "peru", "and", "the"}  # fmt: skip
GENERIC = set().union(*GENERIC_BY_CATEGORY.values()) | FILLER

# "|", "/", "(", ")", " - ", "–", "—", ",", "·" and a lone lowercase "l" used as a pipe.
SEPARATORS = re.compile(r"\s*(?:\||/|\(|\)|\s-\s|\s–\s|\s—\s|,|·|\sl\s)\s*")
MIN_LENGTH = 4
# A one-word alias must look like a brand ("Americadent"), not a common word ("Alemana").
MIN_SINGLE_WORD = 8
CATEGORY_WORDS = set().union(*GENERIC_BY_CATEGORY.values())


class AliasError(ValueError):
    pass


def fold(text: str) -> str:
    """Lowercase, strip accents and punctuation: the form used to compare names."""
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", plain).strip()


def is_generic(text: str) -> bool:
    words = fold(text).split()
    return not words or all(w in GENERIC for w in words)


def _can_drop(words: list[str]) -> bool:
    remaining = words[1:] if words else []
    return len(remaining) >= 2 or (
        len(remaining) == 1 and len(fold(remaining[0])) >= MIN_SINGLE_WORD
    )


def _specific_core(part: str) -> str:
    """Drop leading category words and trailing filler words (districts, "sede"),
    never leaving a short single word."""
    words = part.split()
    while words and fold(words[0]) in CATEGORY_WORDS and _can_drop(words):
        words.pop(0)
    while words and fold(words[-1]) in FILLER and _can_drop(words[::-1]):
        words.pop()
    return " ".join(words)


def derive_aliases(name: str) -> list[str]:
    """Candidate aliases from a Maps name, without generic ones or the full name itself."""
    candidates: list[str] = []
    for part in SEPARATORS.split(name):
        part = part.strip(" .·-")
        if not part:
            continue
        specific = _specific_core(part)
        for candidate in (part, specific):
            if (
                candidate
                and not is_generic(candidate)
                and len(fold(candidate)) >= MIN_LENGTH
                and fold(candidate) != fold(name)
                and fold(candidate) not in {fold(c) for c in candidates}
            ):
                candidates.append(candidate)
    # Keep only the most specific form when one alias contains another ("Centro X" vs "X").
    return [c for c in candidates if not any(c != o and fold(o) in fold(c) for o in candidates)]


def add_alias(conn: psycopg.Connection, clinic_id: int, alias: str) -> bool:
    """Returns False if the clinic already had it (case/accent-insensitive on lower())."""
    alias = alias.strip()
    if len(fold(alias)) < 2:
        raise AliasError("El alias es demasiado corto")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("select 1 from public.clinics where id = %s", (clinic_id,))
        if cur.fetchone() is None:
            raise AliasError(f"No existe la clínica {clinic_id}")
        cur.execute(
            "insert into public.aliases (clinic_id, alias) values (%s, %s) "
            "on conflict (clinic_id, lower(alias)) do nothing returning id",
            (clinic_id, alias),
        )
        return cur.fetchone() is not None


def add_derived_aliases(conn: psycopg.Connection, clinic_id: int, name: str) -> int:
    return sum(add_alias(conn, clinic_id, alias) for alias in derive_aliases(name))


def list_aliases(conn: psycopg.Connection, clinic_id: int) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select alias from public.aliases where clinic_id = %s order by lower(alias)",
            (clinic_id,),
        )
        return [row[0] for row in cur.fetchall()]


def remove_alias(conn: psycopg.Connection, clinic_id: int, alias: str) -> bool:
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "delete from public.aliases where clinic_id = %s and lower(alias) = lower(%s)",
            (clinic_id, alias.strip()),
        )
        return cur.rowcount > 0
