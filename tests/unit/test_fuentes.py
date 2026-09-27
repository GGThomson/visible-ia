import pytest

from visible_ia.extractor.fuentes import SOURCE_TYPES, classify, known_domains


@pytest.mark.parametrize(
    "source, expected",
    [
        # Domains named by the plan (phase-1 sample).
        ("https://www.doctoralia.pe/implantologia/lima", "doctoralia"),
        ("https://www.instagram.com/clinica.x/", "social"),
        ("https://m.facebook.com/odontologicolarco", "social"),
        ("https://elcomercio.pe/tecnologia/nota", "press"),
        ("https://www.fresha.com/es/a/clinica", "directory"),
        ("https://www.whatclinic.com/dentists/peru", "directory"),
        ("dentum.com.pe", "own_website"),
        ("https://topsmile.com.pe/estetica-dental/", "own_website"),
        ("https://www.dentalkrebs.com/tratamientos-dentales", "own_website"),
        ("https://dermatica.pe/", "own_website"),
        ("https://mediesthetic.com.pe/", "own_website"),
        # Run 1 (prod).
        ("https://www.google.com/searchviewer/10?svid=CAwS", "google_profile"),
        ("https://maps.google.com/?cid=123", "google_profile"),
        ("https://sites.google.com/view/clinica", "other"),
        ("https://www.limadentalrating.com/es/", "directory"),
        ("https://www.dentaldepartures.com/dentist/x", "directory"),
        ("https://smilesperu.com/es/", "own_website"),
        ("https://implantes.maxiloface.pe/", "own_website"),
        ("https://www.gob.pe/institucion/minsa", "other"),
        ("https://odontologia.usmp.edu.pe/", "other"),
        ("https://www.cmp.org.pe/", "other"),
        ("https://pmc.ncbi.nlm.nih.gov/articles/x", "other"),
        ("https://es.wikipedia.org/wiki/Implante_dental", "other"),
        ("https://tiemporeal.com.pe/nota", "other"),
        ("", "other"),
    ],
)
def test_classify_cases(source, expected):
    assert classify(source) == expected


def test_market_clinic_website_is_own_website():
    websites = {"https://www.kagem.pe/", "clinica-sin-palabras-clave.pe"}
    assert classify("https://kagem.pe/implantes", websites) == "own_website"
    assert classify("https://clinica-sin-palabras-clave.pe/x", websites) == "own_website"
    assert classify("https://kagem.pe/implantes") == "other"  # not known without the market


def test_longest_suffix_wins():
    assert classify("https://sites.google.com/x") == "other"
    assert classify("https://www.google.com/maps/place/x") == "google_profile"


def test_table_only_uses_valid_types():
    assert set(known_domains().values()) <= set(SOURCE_TYPES)
    assert SOURCE_TYPES == (
        "google_profile",
        "doctoralia",
        "own_website",
        "social",
        "directory",
        "press",
        "other",
    )
