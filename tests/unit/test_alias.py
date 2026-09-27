import pytest

from visible_ia.mercados.alias import derive_aliases, fold, is_generic


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        # Real Maps names from the 26/09 sample
        ("Implantes Dental | Perez Yance / Clínicas Dentales Americadent",
         ["Perez Yance", "Americadent"]),
        ("Mejor Clínica Dental en Miraflores - Implantes Dentales en miraflores"
         " - Enmanuel Teixeira",
         ["Enmanuel Teixeira"]),
        ("Medi Esthetic Surco l Medicina Estetica - Dermatología - Depilación Laser",
         ["Medi Esthetic"]),
        ("Clínica Odontologists Miraflores", ["Odontologists"]),
        ("Clínica Lima Derma", ["Lima Derma"]),
        ("Clínica Dental Alemana", ["Dental Alemana"]),  # "Alemana" alone is too common
        ("Smiles Peru", []),  # nothing to add: the name itself is already specific
        ("CLÍNICA DE LA PIEL", []),  # fully generic parts are never aliases
    ],
)  # fmt: skip
def test_derive_aliases_real_names(name, expected):
    assert derive_aliases(name) == expected


@pytest.mark.parametrize(
    "text",
    ["Clínica Dental", "Implantes Dentales", "Dermatología", "Implantes Dental",
     "Mejor Clínica Dental en Miraflores", "Sede Surco"],
)  # fmt: skip
def test_generic_phrases_are_detected(text):
    assert is_generic(text)


def test_fold_removes_accents_case_and_punctuation():
    assert fold("  Pérez-Yance, S.A.C. ") == "perez yance s a c"


def test_repeated_parts_give_one_alias():
    assert derive_aliases("Perez Yance | Perez Yance") == ["Perez Yance"]


def test_alias_never_equals_full_name():
    assert derive_aliases("Clínica Americadent") == ["Americadent"]
    assert derive_aliases("Americadent") == []
