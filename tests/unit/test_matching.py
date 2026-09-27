import pytest

from visible_ia.extractor.matching import ClinicCandidate, match, specific

# Names as they come from Google Maps (phase-1 sample and run 1), with their aliases.
CLINICS = [
    ClinicCandidate(
        1,
        "Implantes Dental | Perez Yance / Clínicas Dentales Americadent",
        ("Perez Yance", "Americadent"),
    ),
    ClinicCandidate(
        2,
        "Mejor Clínica Dental en Miraflores - Implantes Dentales en miraflores - Enmanuel Teixeira",
        ("Enmanuel Teixeira",),
    ),
    ClinicCandidate(3, "Smiles Peru"),
    ClinicCandidate(4, "Digital Smiles"),
    ClinicCandidate(5, "Clínica Dental Cano"),
    ClinicCandidate(6, "Dr. Aldo | Implantes Dentales y Rehabilitación Oral", ("Dr. Aldo",)),
]


@pytest.mark.parametrize(
    "mention, status, clinic_id",
    [
        # Cases required by the plan (C4-T02).
        ("Perez Yance", "matched", 1),
        ("Implantes Dental | Perez Yance / Clínicas Dentales Americadent", "matched", 1),
        ("Dr. Enmanuel Teixeira", "matched", 2),
        ("RenovaSmiles Perú", "new", None),  # false positive seen in phase 1
        # More real forms from run 1.
        ("Dental Pérez Yance", "matched", 1),
        ("Smiles Perú", "matched", 3),
        ("SMILES PERU", "matched", 3),
        ("Clínica Dental Cano", "matched", 5),
        ("Cano Dental", "matched", 5),
        ("Dr. Aldo Implants", "matched", 6),
        ("Odontonova", "new", None),
        ("Clínica Dental", "new", None),  # only generic words
        ("Clínica Miraflores", "new", None),
        ("", "new", None),
    ],
)
def test_match_cases(mention, status, clinic_id):
    result = match(mention, CLINICS)
    assert (result.status, result.clinic_id) == (status, clinic_id)


def test_exact_match_is_marked_as_exact():
    result = match("Perez Yance", CLINICS)
    assert result.via == "exact" and result.score == 100


def test_a_tie_goes_to_review_never_to_two_clinics():
    result = match("Smiles", CLINICS)
    assert result.status == "review"
    assert result.clinic_id is None
    assert result.tied == (3, 4)


def test_two_clinics_sharing_an_exact_alias_go_to_review():
    clinics = [ClinicCandidate(1, "Clínica Sol", ("Sol Dental",)), ClinicCandidate(2, "Sol Dental")]
    result = match("Sol Dental", clinics)
    assert result.status == "review" and result.tied == (1, 2)


def test_threshold_is_configurable():
    assert match("Digital Smile", CLINICS).clinic_id == 4
    assert match("Digital Smile", CLINICS, threshold=99).status == "new"


def test_specific_drops_generic_words_districts_and_titles():
    assert specific("Dra. Clínica Dental Pérez Yance - Miraflores") == "perez yance"
