import pytest

from visible_ia.puntaje.brecha import has_gap
from visible_ia.puntaje.fuentes import top_sources, type_shares


@pytest.mark.parametrize(
    "rating, reviews, index, expected",
    [
        (4.9, 1135, 10.0, True),  # well rated, many reviews, almost absent
        (4.9, 1135, 10.1, False),
        (4.4, 1135, 0.0, False),  # rating below 4.5
        (4.8, 99, 0.0, False),  # fewer than 100 reviews
        (4.5, 100, 0.0, True),  # exactly at the thresholds
        (None, 500, 0.0, False),  # no Maps data
        (4.8, None, 0.0, False),
    ],
)
def test_gap_criterion(rating, reviews, index, expected):
    assert has_gap(rating, reviews, index) is expected


def test_gap_thresholds_are_configurable():
    assert has_gap(4.6, 60, 5.0, min_reviews=50) is True
    assert has_gap(4.6, 150, 15.0, max_index=20) is True


CITATIONS = [
    (1, "chatgpt_api", "smilesperu.com", "own_website"),
    (1, "chatgpt_api", "smilesperu.com", "own_website"),  # same answer: counts once
    (1, "chatgpt_api", "doctoralia.pe", "doctoralia"),
    (2, "chatgpt_api", "smilesperu.com", "own_website"),
    (3, "google_ai_mode", "google.com", "google_profile"),
    (4, "google_ai_mode", "google.com", "google_profile"),
    (4, "google_ai_mode", "doctoralia.pe", "doctoralia"),
]


def test_top_sources_by_type_with_share_of_answers():
    top = top_sources(CITATIONS, total_answers=4)
    assert list(top) == ["google_profile", "doctoralia", "own_website"]
    own = top["own_website"][0]
    assert (own.domain, own.answers, own.share) == ("smilesperu.com", 2, 50.0)
    assert own.by_surface == {"chatgpt_api": 2, "google_ai_mode": 0}
    doc = top["doctoralia"][0]
    assert doc.by_surface == {"chatgpt_api": 1, "google_ai_mode": 1}


def test_top_sources_keeps_the_top_n_per_type():
    many = [(i, "chatgpt_api", f"clinica{i}.pe", "own_website") for i in range(10)]
    assert len(top_sources(many, 10, per_type=3)["own_website"]) == 3


def test_type_shares():
    assert type_shares(CITATIONS, 4) == {
        "own_website": 50.0,
        "doctoralia": 50.0,
        "google_profile": 50.0,
    }
