# disc-decode

One person takes a 24-tetrad forced-choice questionnaire, answers save to
SQLite, they see their DISC profile. That is the entire app.

## Source of truth
- docs/spec.md holds the scoring rules, data model, validation, and pages.
- If the spec is silent or ambiguous, STOP and ask. Never invent scoring
  behavior, tie handling, or validation rules.

## Scope discipline
This project was previously scoped as a multiplayer game and deliberately cut
back. Do not add teams, guessing, timers, multiplayer, accounts, or admin
views. If a change seems to need one of those, say so instead of building it.

## Who I am
I am returning to hands-on coding after 20 years away. Explain your reasoning
in plain language. Prefer boring, obvious code over clever code. When you use
a Python or FastAPI idiom I may not know, add a one-line comment saying what
it does. Never add a library without telling me why it is needed.
Prefer the simplest thing that works and passes tests. Do not add features,
abstractions, or configuration I did not ask for.

## Everything runs in Docker
- make up | make test | make lint | make fmt | make fill | make sh
- Never tell me to run python, pip, or uvicorn directly on my machine.
- Tests and lint must pass before any commit.

## Architecture
- FastAPI with plain `def` endpoints. No async — we do not need it.
- Jinja2 templates render HTML server-side. Plain forms; HTMX only if it
  genuinely simplifies something.
- SQLite via the stdlib sqlite3 module. Plain SQL, no ORM.
- Signed session cookies for identity (Starlette SessionMiddleware).
- Database path comes from the DB_PATH environment variable.

## Non-negotiable rules
- SQL uses ? placeholders ALWAYS. Never f-strings or concatenation in SQL.
- Scoring runs server-side only. Never compute or trust scores in the browser.
- Validate every write: tetrad index in 0-23, both styles in D/I/S/C, and
  most != least. Reject before touching the database.
- A respondent can only read and write their own rows. Check the session
  token on every route that touches respondent data.
- Ties produce a SET of styles, never an arbitrary single pick.
- The four difference scores must always sum to zero. There is a test for
  this; do not weaken it.
- Questionnaire text in app/logic/items.py is ORIGINAL and stays that way.
  Never replace it with items from a commercial DISC instrument — that text
  is copyrighted. Do not move the items into the database.
- Never commit the .db file, secrets, or real people's names.

## Conventions
- Scoring and other game logic live in app/logic/ as pure functions with no
  database access, so they can be tested directly. Routes stay thin.
- Tests live in tests/, named test_<thing>.py.
- Scoring tests use hand-checked fixtures with expected values worked out by
  hand. Never generate the expected value using the function under test.
- Type hints on function signatures.

## Definition of done
Tests pass, lint passes, it works in the browser on a phone-sized window, the
acceptance criteria on the phase's GitHub issue are met, and CodeRabbit
reports no critical or major findings.