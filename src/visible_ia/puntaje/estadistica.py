"""Statistics for the presence index, in pure Python (no scipy): PRD §5.2 and §5.5, ADR-003.

- Wilson interval for a proportion (the "margin of variation" shown with every index).
- Two-proportion z-test (pooled, two-sided) for the month-to-month change of the combined index.
- Detectable difference: the smallest rise that a two-proportion test can report from level p
  with n answers per period, z·√(2p(1−p)/n). It reproduces the PRD §5.5 table (30 % with
  n = 30 → ≈ 23 points).

Proportions are 0–1 here; callers turn them into 0–100 points. n = 0 means "no data": the
functions return None instead of inventing a number.
"""

import math

Z_95 = 1.959963984540054  # two-sided 95 %


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def wilson(k: int, n: int, z: float = Z_95) -> tuple[float, float] | None:
    """95 % Wilson interval for k successes out of n (None when n = 0)."""
    if n <= 0:
        return None
    if not 0 <= k <= n:
        raise ValueError(f"k fuera de rango: {k} de {n}")
    p = k / n
    z2 = z * z
    center = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    low = 0.0 if k == 0 else max(0.0, center - half)
    high = 1.0 if k == n else min(1.0, center + half)
    return low, high


def dos_proporciones(k1: int, n1: int, k2: int, n2: int) -> tuple[float, float] | None:
    """Pooled two-sided z-test of p2 vs p1: (z, p-value). z > 0 means p2 is higher.

    None when a period has no data. When both proportions are 0 or both are 1 there is no
    variance: z = 0 and p-value = 1 (no change).
    """
    if n1 <= 0 or n2 <= 0:
        return None
    p1, p2 = k1 / n1, k2 / n2
    pooled = (k1 + k2) / (n1 + n2)
    variance = pooled * (1 - pooled) * (1 / n1 + 1 / n2)
    if variance == 0:
        return 0.0, 1.0
    z = (p2 - p1) / math.sqrt(variance)
    return z, 2 * (1 - normal_cdf(abs(z)))


def diferencia_detectable(p: float, n: int, z: float = Z_95) -> float | None:
    """Smallest reportable change (0–1) from level p with n answers in each period."""
    if n <= 0:
        return None
    if not 0 <= p <= 1:
        raise ValueError(f"p fuera de rango: {p}")
    return z * math.sqrt(2 * p * (1 - p) / n)
