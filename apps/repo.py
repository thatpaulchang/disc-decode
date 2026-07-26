import secrets
import sqlite3

from apps.db import get_connection
from apps.logic.scoring import Answer, Score, score_answers


def create_respondent(display_name: str) -> str:
    token = secrets.token_urlsafe(32)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO respondents (token, display_name) VALUES (?, ?)",
            (token, display_name),
        )
        conn.commit()
    finally:
        conn.close()
    return token


def get_respondent_by_token(token: str) -> sqlite3.Row | None:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM respondents WHERE token = ?", (token,)).fetchone()
    finally:
        conn.close()


def save_answer(respondent_id: int, tetrad_index: int, most_style: str, least_style: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO responses (respondent_id, tetrad_index, most_style, least_style)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (respondent_id, tetrad_index)
            DO UPDATE SET most_style = excluded.most_style, least_style = excluded.least_style
            """,
            (respondent_id, tetrad_index, most_style, least_style),
        )
        conn.commit()
    finally:
        conn.close()


def get_answers(respondent_id: int) -> dict[int, sqlite3.Row]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM responses WHERE respondent_id = ?", (respondent_id,)
        ).fetchall()
    finally:
        conn.close()
    return {row["tetrad_index"]: row for row in rows}


def first_unanswered_tetrad(respondent_id: int, total_tetrads: int) -> int | None:
    answered = get_answers(respondent_id).keys()
    for index in range(total_tetrads):
        if index not in answered:
            return index
    return None


def save_results(respondent_id: int, score: Score) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO results (
                respondent_id,
                most_d, most_i, most_s, most_c,
                least_d, least_i, least_s, least_c,
                diff_d, diff_i, diff_s, diff_c,
                top_styles, bottom_styles
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (respondent_id) DO UPDATE SET
                most_d = excluded.most_d, most_i = excluded.most_i,
                most_s = excluded.most_s, most_c = excluded.most_c,
                least_d = excluded.least_d, least_i = excluded.least_i,
                least_s = excluded.least_s, least_c = excluded.least_c,
                diff_d = excluded.diff_d, diff_i = excluded.diff_i,
                diff_s = excluded.diff_s, diff_c = excluded.diff_c,
                top_styles = excluded.top_styles,
                bottom_styles = excluded.bottom_styles,
                completed_at = datetime('now')
            """,
            (
                respondent_id,
                score.most["D"],
                score.most["I"],
                score.most["S"],
                score.most["C"],
                score.least["D"],
                score.least["I"],
                score.least["S"],
                score.least["C"],
                score.diff["D"],
                score.diff["I"],
                score.diff["S"],
                score.diff["C"],
                ",".join(sorted(score.top_styles)),
                ",".join(sorted(score.bottom_styles)),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_results(respondent_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM results WHERE respondent_id = ?", (respondent_id,)
        ).fetchone()
    finally:
        conn.close()


def reset_respondent(respondent_id: int) -> None:
    """Delete this respondent's answers and results so they can retake the
    questionnaire from scratch. The respondent row (and its session token)
    is kept as-is."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM responses WHERE respondent_id = ?", (respondent_id,))
        conn.execute("DELETE FROM results WHERE respondent_id = ?", (respondent_id,))
        conn.commit()
    finally:
        conn.close()


def compute_and_save_results(respondent_id: int, total_tetrads: int) -> sqlite3.Row:
    """Score the respondent's current answers and persist the result.

    Always recomputes from the current responses rather than reusing a
    stored row, so that going back and changing an answer after reaching
    /results is reflected the next time /results is viewed. Caller must
    already know all tetrads are answered (i.e. first_unanswered_tetrad
    returned None) -- this does not check.
    """
    answers_by_index = get_answers(respondent_id)
    answers = [
        Answer(answers_by_index[i]["most_style"], answers_by_index[i]["least_style"])
        for i in range(total_tetrads)
    ]
    save_results(respondent_id, score_answers(answers))
    return get_results(respondent_id)
