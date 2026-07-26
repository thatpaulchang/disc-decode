import sqlite3

from fastapi import Request

from apps.repo import create_respondent, get_respondent_by_token

SESSION_KEY = "token"


def get_or_create_respondent(request: Request, display_name: str | None = None) -> sqlite3.Row:
    """Look up the respondent for this session, creating one if needed.

    display_name is only used the first time, when a new respondent is created.
    """
    token = request.session.get(SESSION_KEY)
    respondent = get_respondent_by_token(token) if token else None
    if respondent is not None:
        return respondent

    token = create_respondent(display_name or "Anonymous")
    request.session[SESSION_KEY] = token
    return get_respondent_by_token(token)


def get_current_respondent(request: Request) -> sqlite3.Row | None:
    """Look up the respondent for this session without creating one."""
    token = request.session.get(SESSION_KEY)
    return get_respondent_by_token(token) if token else None
