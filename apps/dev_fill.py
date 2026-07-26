"""Dev helper: create a respondent with 24 random valid answers.

Run via `make fill`. Prints a ready-to-paste session cookie so you can jump
straight to /results in a browser without clicking through the questionnaire.
"""

import json
import os
import random
from base64 import b64encode

import itsdangerous

from apps.db import init_db
from apps.logic.items import TETRADS
from apps.repo import create_respondent, get_respondent_by_token, save_answer
from apps.session import SESSION_KEY

STYLES = ["D", "I", "S", "C"]


def sign_session_cookie(token: str) -> str:
    """Build the same signed cookie value Starlette's SessionMiddleware would set.

    Must match apps.main's SessionMiddleware byte-for-byte: standard (padded)
    base64 signed with itsdangerous.TimestampSigner, same as Starlette uses
    internally -- itsdangerous's own base64 helpers are unpadded and won't
    round-trip through Starlette's decoder.
    """
    signer = itsdangerous.TimestampSigner(os.environ["SESSION_SECRET"])
    payload = {SESSION_KEY: token}
    data = b64encode(json.dumps(payload).encode("utf-8"))
    return signer.sign(data).decode("utf-8")


def main() -> None:
    init_db()
    token = create_respondent("Dev Fixture")
    respondent = get_respondent_by_token(token)

    for tetrad_index in range(len(TETRADS)):
        most_style, least_style = random.sample(STYLES, 2)
        save_answer(respondent["id"], tetrad_index, most_style, least_style)

    cookie_value = sign_session_cookie(token)
    print(f"Created respondent id={respondent['id']} with {len(TETRADS)} random answers.")
    print()
    print("To view /results in a browser, set a cookie named 'session' to:")
    print(cookie_value)
    print()
    print("Or from the command line:")
    print(f"  curl --cookie 'session={cookie_value}' http://localhost:8000/results")


if __name__ == "__main__":
    main()
