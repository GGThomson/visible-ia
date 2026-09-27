from datetime import date

import pytest

from visible_ia.puntaje.indice import Score, apply_change_rule, change_label, month_shift

OCT = date(2026, 10, 1)


def _score(k, n=60, surface="combined", clinic=1):
    return Score(clinic, surface, n, k, round(100 * k / n, 2), None, None, None, None)


def test_month_shift_crosses_years():
    assert month_shift(date(2026, 1, 1), -1) == date(2025, 12, 1)
    assert month_shift(date(2026, 11, 1), 2) == date(2027, 1, 1)


@pytest.mark.parametrize(
    "prev, k, expected",
    [
        ((18, 60), 36, "up"),  # 30 % -> 60 %: clear rise
        ((18, 60), 22, "no_clear_change"),  # 30 % -> 37 %: noise with 60 answers
        ((36, 60), 18, "down"),  # 60 % -> 30 %: clear fall
        (None, 20, "first_month"),
        ((0, 0), 20, "first_month"),
    ],
)
def test_change_label_uses_the_two_proportion_test(prev, k, expected):
    assert change_label(prev, k, 60) == expected


def test_change_is_only_for_the_combined_index():
    scores = [_score(36), _score(20, 30, "chatgpt_api")]
    history = {
        (1, "combined", date(2026, 9, 1)): (18, 60),
        (1, "chatgpt_api", date(2026, 9, 1)): (5, 30),
    }
    combined, chatgpt = apply_change_rule(scores, OCT, history)
    assert combined.change == "up"
    assert chatgpt.change is None  # per surface: only the 3-month window (ADR-003)


def test_window_with_one_two_and_three_months():
    first = apply_change_rule([_score(18)], OCT, {})[0]
    assert (first.window3_index, first.change) == (30.0, "first_month")

    two = apply_change_rule([_score(18)], OCT, {(1, "combined", date(2026, 9, 1)): (12, 60)})[0]
    assert two.window3_index == 25.0  # (18 + 12) / 120

    history = {
        (1, "combined", date(2026, 9, 1)): (12, 60),
        (1, "combined", date(2026, 8, 1)): (6, 60),
        (1, "combined", date(2026, 7, 1)): (60, 60),  # 4 months ago: outside the window
    }
    three = apply_change_rule([_score(18)], OCT, history)[0]
    assert three.window3_index == 20.0  # (18 + 12 + 6) / 180
    assert three.window3_ci_low < 20.0 < three.window3_ci_high


def test_detectable_difference_is_stored_in_points():
    s = apply_change_rule([_score(18)], OCT, {})[0]
    assert round(s.detectable_diff) == 16  # 30 % with 60 answers (PRD §5.5)
    zero = apply_change_rule([_score(0)], OCT, {})[0]
    assert zero.detectable_diff > 0  # at 0 % it starts from one appearance
