import secrets
import sqlite3

from apps.db import get_connection


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
