import pytest

from visible_ia.puntaje.estadistica import (
    diferencia_detectable,
    dos_proporciones,
    normal_cdf,
    wilson,
)


@pytest.mark.parametrize(
    "k, n, low, high",
    [
        # PRD §5.5 table (rounded to whole points there).
        (9, 30, 0.1666, 0.4788),  # 30 % with n = 30 -> 17–48 %
        (3, 30, 0.0346, 0.2562),  # 10 % -> 3–26 %
        (15, 30, 0.3315, 0.6685),  # 50 % -> 33–67 %
        (18, 60, 0.1990, 0.4251),  # 30 % with n = 60 -> 20–43 %
        (27, 90, 0.2151, 0.4013),  # 30 % with n = 90 -> 22–40 %
        # Other values. All rows verified with statsmodels proportion_confint(method="wilson")
        # on 27/09/2026 (not a project dependency).
        (1, 10, 0.0179, 0.4042),
        (45, 50, 0.7864, 0.9565),
    ],
)
def test_wilson_matches_known_values(k, n, low, high):
    lo, hi = wilson(k, n)
    assert lo == pytest.approx(low, abs=5e-4)
    assert hi == pytest.approx(high, abs=5e-4)


def test_wilson_edge_cases():
    lo, hi = wilson(0, 30)
    assert lo == 0 and hi == pytest.approx(0.1135, abs=5e-4)
    lo, hi = wilson(30, 30)
    assert lo == pytest.approx(0.8865, abs=5e-4) and hi == 1
    assert wilson(0, 0) is None
    with pytest.raises(ValueError):
        wilson(31, 30)


@pytest.mark.parametrize(
    "p, n, points",
    [(0.30, 30, 23), (0.30, 60, 16), (0.30, 90, 13), (0.30, 150, 10)],  # PRD §5.5
)
def test_detectable_difference_reproduces_the_prd_table(p, n, points):
    assert round(diferencia_detectable(p, n) * 100) == points


def test_detectable_difference_edge_cases():
    assert diferencia_detectable(0.3, 0) is None
    assert diferencia_detectable(0.0, 30) == 0
    with pytest.raises(ValueError):
        diferencia_detectable(1.2, 30)


def test_two_proportions_known_value():
    # 9/30 -> 18/30: z = 2.335, p = 0.0195 (verified with statsmodels proportions_ztest).
    z, p = dos_proporciones(9, 30, 18, 30)
    assert z == pytest.approx(2.335, abs=1e-3)
    assert p == pytest.approx(0.0196, abs=1e-3)


def test_two_proportions_direction_and_noise():
    z, p = dos_proporciones(18, 60, 12, 60)
    assert z < 0 and p > 0.05  # 30 % -> 20 %: not a clear change with 60 answers
    z, p = dos_proporciones(10, 60, 10, 60)
    assert z == 0 and p == pytest.approx(1.0)


def test_two_proportions_edge_cases():
    assert dos_proporciones(0, 30, 0, 30) == (0.0, 1.0)
    assert dos_proporciones(30, 30, 30, 30) == (0.0, 1.0)
    assert dos_proporciones(0, 0, 5, 30) is None
    z, p = dos_proporciones(0, 30, 6, 30)
    assert z > 0 and p < 0.05


def test_normal_cdf():
    assert normal_cdf(0) == pytest.approx(0.5)
    assert normal_cdf(1.959963984540054) == pytest.approx(0.975, abs=1e-9)
