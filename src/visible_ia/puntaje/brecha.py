"""Maps vs AI gap (HU-13): well rated on Google Maps but almost absent from the AI answers.

A clinic has a gap when its rating >= 4.5, its reviews >= 100 and its combined index <= 10 %
(H4 criterion from phase 1). The thresholds are configurable. The rating and reviews carry
the date they were taken, because they change over time.
"""

from dataclasses import dataclass
from datetime import date

import psycopg

from visible_ia.puntaje.indice import ScoreError

MIN_RATING = 4.5
MIN_REVIEWS = 100
MAX_INDEX = 10.0


@dataclass(frozen=True)
class GapRow:
    clinic_id: int
    name: str
    rating: float | None
    reviews: int | None
    data_date: date | None
    combined_index: float
    gap: bool


def has_gap(
    rating: float | None,
    reviews: int | None,
    index: float,
    *,
    min_rating: float = MIN_RATING,
    min_reviews: int = MIN_REVIEWS,
    max_index: float = MAX_INDEX,
) -> bool:
    if rating is None or reviews is None:
        return False
    return rating >= min_rating and reviews >= min_reviews and index <= max_index


def gap_table(
    conn: psycopg.Connection,
    market_id: int,
    month: date | None = None,
    *,
    min_rating: float = MIN_RATING,
    min_reviews: int = MIN_REVIEWS,
    max_index: float = MAX_INDEX,
) -> tuple[date, list[GapRow]]:
    with conn.cursor() as cur:
        if month is None:
            cur.execute(
                "select max(month) from public.monthly_scores where market_id = %s", (market_id,)
            )
            month = cur.fetchone()[0]
            if month is None:
                raise ScoreError(f"El mercado {market_id} no tiene puntajes: calcula una corrida")
        cur.execute(
            "select c.id, c.name, c.rating, c.review_count, c.data_date, s.presence_index "
            "from public.monthly_scores s join public.clinics c on c.id = s.clinic_id "
            "where s.market_id = %s and s.month = %s and s.surface = 'combined'",
            (market_id, month),
        )
        rows = []
        for clinic_id, name, rating, reviews, data_date, index in cur.fetchall():
            rating = None if rating is None else float(rating)
            index = float(index)
            gap = has_gap(
                rating, reviews, index,
                min_rating=min_rating, min_reviews=min_reviews, max_index=max_index,
            )  # fmt: skip
            rows.append(GapRow(clinic_id, name, rating, reviews, data_date, index, gap))
    rows.sort(key=lambda r: (not r.gap, -(r.reviews or 0)))
    return month, rows
