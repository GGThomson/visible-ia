import pytest

from visible_ia.puntaje.indice import Answer, MentionRow, compute_scores

A, B, C = 1, 2, 3  # market clinics; None = a clinic outside the market


def _run():
    """10 ChatGPT answers (ids 1–10) and 10 Google answers (ids 11–20)."""
    answers = [Answer(i, "chatgpt_api") for i in range(1, 11)]
    answers += [Answer(i, "google_ai_mode") for i in range(11, 21)]
    mentions = []
    # ChatGPT: A in 4 answers (position 1), B in 2 answers (after an outside clinic).
    for r in (1, 2, 3, 4):
        mentions.append(MentionRow(r, 1, A))
    for r in (1, 2):
        mentions.append(MentionRow(r, 2, None))
        mentions.append(MentionRow(r, 3, B))
    # Google: A in 1 answer at rank 2, B in 5 answers at rank 1.
    mentions.append(MentionRow(11, 1, B))
    mentions.append(MentionRow(11, 2, A))
    for r in (12, 13, 14, 15):
        mentions.append(MentionRow(r, 1, B))
    return answers, mentions


def _by(scores):
    return {(s.clinic_id, s.surface): s for s in scores}


def test_index_per_surface_and_combined():
    s = _by(compute_scores(*_run(), [A, B, C]))
    assert (s[A, "chatgpt_api"].appearances, s[A, "chatgpt_api"].presence_index) == (4, 40.0)
    assert (s[A, "google_ai_mode"].appearances, s[A, "google_ai_mode"].presence_index) == (1, 10.0)
    assert s[A, "combined"].presence_index == 25.0  # (40 + 10) / 2
    assert (s[A, "combined"].n_responses, s[A, "combined"].appearances) == (20, 5)
    assert s[B, "combined"].presence_index == 35.0  # (20 + 50) / 2


def test_wilson_interval_is_stored_in_points():
    s = _by(compute_scores(*_run(), [A, B, C]))
    assert s[A, "chatgpt_api"].ci_low == pytest.approx(16.82, abs=0.01)
    assert s[A, "chatgpt_api"].ci_high == pytest.approx(68.73, abs=0.01)


def test_average_position_counts_names_in_order():
    s = _by(compute_scores(*_run(), [A, B, C]))
    assert s[A, "chatgpt_api"].avg_position == 1.0
    assert s[B, "chatgpt_api"].avg_position == 3.0  # after A and an outside clinic
    assert s[A, "google_ai_mode"].avg_position == 2.0
    assert s[B, "combined"].avg_position == pytest.approx((3 + 3 + 1 * 5) / 7, abs=0.01)


def test_share_of_mentions_among_market_clinics():
    s = _by(compute_scores(*_run(), [A, B, C]))
    assert s[A, "chatgpt_api"].mention_share == pytest.approx(66.67, abs=0.01)  # 4 / 6
    assert s[B, "google_ai_mode"].mention_share == pytest.approx(83.33, abs=0.01)  # 5 / 6
    assert s[A, "combined"].mention_share == pytest.approx(41.67, abs=0.01)  # 5 / 12


def test_clinic_without_appearances_scores_zero():
    s = _by(compute_scores(*_run(), [A, B, C]))
    for surface in ("chatgpt_api", "google_ai_mode", "combined"):
        assert s[C, surface].presence_index == 0
        assert s[C, surface].ci_low == 0
        assert s[C, surface].avg_position is None


def test_a_clinic_named_twice_in_one_answer_counts_once():
    answers = [Answer(1, "chatgpt_api"), Answer(2, "google_ai_mode")]
    mentions = [MentionRow(1, 1, A), MentionRow(1, 2, A)]
    s = _by(compute_scores(answers, mentions, [A]))
    assert s[A, "chatgpt_api"].appearances == 1
    assert s[A, "chatgpt_api"].avg_position == 1.0


def test_surface_without_answers_is_left_out_of_the_combined():
    answers = [Answer(1, "chatgpt_api"), Answer(2, "chatgpt_api")]
    s = _by(compute_scores(answers, [MentionRow(1, 1, A)], [A]))
    assert s[A, "google_ai_mode"].n_responses == 0 and s[A, "google_ai_mode"].ci_low is None
    assert s[A, "combined"].presence_index == 50.0
