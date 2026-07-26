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
            ON CONFLICT (respondent_id) DO NOTHING
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


def get_or_create_results(respondent_id: int, total_tetrads: int) -> sqlite3.Row:
    """Fetch stored results, scoring and saving them first if this is the
    first time this respondent has reached /results.

    Caller must already know all tetrads are answered (i.e.
    first_unanswered_tetrad returned None) -- this does not check.
    """
    results = get_results(respondent_id)
    if results is not None:
        return results

    answers_by_index = get_answers(respondent_id)
    answers = [
        Answer(answers_by_index[i]["most_style"], answers_by_index[i]["least_style"])
        for i in range(total_tetrads)
    ]
    save_results(respondent_id, score_answers(answers))
    return get_results(respondent_id)
