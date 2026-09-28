import re

import pytest

from visible_ia.checklist import SiteProfile, load_catalog, prioritize

# Source shares of run 1 (Implantología · Miraflores).
MIRAFLORES = {"own_website": 80, "google_profile": 50, "directory": 28, "doctoralia": 28,
              "other": 27, "social": 5}  # fmt: skip


def _profile(**kw):
    base = dict(
        site_id=1, category="IMP", district="Miraflores", website="https://odontologists.com/",
        instagram="@odontologists", rating=4.9, reviews=1135, type_shares=MIRAFLORES,
        cited_domains={"odontologists.com", "smilesperu.com", "doctoralia.pe"},
    )  # fmt: skip
    base.update(kw)
    return SiteProfile(**base)


def test_established_clinic_gets_only_what_it_lacks():
    codes = [t.code for t in prioritize(_profile())]
    # Many reviews, its web is cited, it has Instagram: no reviews, web or social tasks.
    assert codes == ["ficha_google", "doctoralia", "bing_places"]


def test_new_clinic_gets_the_full_base_order():
    profile = _profile(website=None, instagram=None, reviews=20, rating=4.2,
                       type_shares={"doctoralia": 5}, cited_domains=set())  # fmt: skip
    codes = [t.code for t in prioritize(profile)]
    assert codes == ["ficha_google", "resenas", "web_schema", "redes", "bing_places"]


def test_market_sources_raise_a_task():
    # Where the AI cites own websites a lot, the web task jumps ahead of Doctoralia.
    profile = _profile(website="https://nueva.pe/", cited_domains=set(),
                       type_shares={"own_website": 90, "doctoralia": 12})  # fmt: skip
    codes = [t.code for t in prioritize(profile)]
    assert codes.index("web_schema") < codes.index("doctoralia")


def test_texts_are_filled_in_for_the_site():
    tasks = prioritize(_profile(category="DER", district="Surco", website=None))
    web = next(t for t in tasks if t.code == "web_schema")
    assert web.title == "Una página de dermatología en tu web, con schema"
    assert "{" not in " ".join(t.title + t.detail for t in tasks)
    assert [t.priority for t in tasks] == list(range(1, len(tasks) + 1))


# Recommendations Google forbids (Business Profile guidelines): keywords or the district in
# the business name, fake / bought / incentivised reviews, several profiles for one place.
FORBIDDEN = [
    r"\b(agrega|añade|incluye|pon|usa)\w*\s+(palabras clave|el distrito|la especialidad)"
    r"[^.]*\b(en|a)l?\s+(el\s+|tu\s+)?nombre",
    r"\b(compra|consigue|ofrece)\w*[^.]*reseñas",
    r"\breseñas falsas\b(?![^.]*prohíbe)",
    r"\b(crea|abre)\w*\s+(otra|varias|una segunda)\s+ficha",
]


@pytest.mark.parametrize("task", load_catalog(), ids=lambda t: t["codigo"])
def test_no_task_recommends_practices_google_forbids(task):
    text = f"{task['titulo']}. {task['detalle']}".lower()
    for pattern in FORBIDDEN:
        assert not re.search(pattern, text), (task["codigo"], pattern)


def test_the_profile_task_warns_against_keyword_names():
    ficha = next(t for t in load_catalog() if t["codigo"] == "ficha_google")
    assert "nombre real" in ficha["detalle"] and "prohíbe" in ficha["detalle"]
