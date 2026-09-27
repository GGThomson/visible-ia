import pytest

from visible_ia.motor.corrida import Call, domain_of, normalize_url, plan_of
from visible_ia.motor.presupuesto import RunPlan


@pytest.mark.parametrize(
    "url, expected",
    [
        (
            "https://www.sonrisaandina.pe/implantes?utm_source=openai",
            "https://www.sonrisaandina.pe/implantes",
        ),
        (
            "https://doctoralia.pe/buscar?q=implantes&utm_medium=x&page=2#top",
            "https://doctoralia.pe/buscar?q=implantes&page=2",
        ),
        ("https://clinica.pe/", "https://clinica.pe/"),
    ],
)
def test_normalize_url_drops_utm_and_fragment(url, expected):
    assert normalize_url(url) == expected


@pytest.mark.parametrize(
    "url, domain",
    [
        ("https://www.Sonrisaandina.pe/implantes", "sonrisaandina.pe"),
        ("https://m.facebook.com/x", "m.facebook.com"),
        ("https://www.google.com/searchviewer/10?svid=abc", "google.com"),
        ("not a url", ""),
    ],
)
def test_domain_without_www(url, domain):
    assert domain_of(url) == domain


def test_plan_counts_pending_calls_per_surface():
    calls = [
        Call(1, "IMP-01", "q", "chatgpt_api", 1),
        Call(1, "IMP-01", "q", "chatgpt_api", 2),
        Call(1, "IMP-01", "q", "google_ai_mode", 1),
    ]
    assert plan_of(calls) == RunPlan(chatgpt_calls=2, serpapi_calls=1)
