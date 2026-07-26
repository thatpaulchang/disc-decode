# disc-decode

One person takes a 24-question DISC questionnaire, answers save to SQLite, they see their DISC profile.

This is an unvalidated, for-entertainment questionnaire inspired by the public-domain DISC model first described by William Moulton Marston in *Emotions of Normal People* (1928). It has no validity evidence behind it and is not suitable for hiring, promotion, or performance decisions. Scores are ipsative — they rank your four styles against each other, not against other people. All questionnaire text is original to this project. "DiSC®" and "Everything DiSC®" are registered trademarks of John Wiley & Sons, Inc., which has no connection to this project.

## Running it

Everything runs in Docker. You need Docker installed; nothing else.

```
cp .env.example .env   # first time only
make up                 # build and start the app at http://localhost:8000
```

## Other commands

| Command | Does |
|---|---|
| `make up` | Build and run the app |
| `make test` | Run the test suite |
| `make lint` | Check code style with ruff |
| `make fmt` | Auto-format code with ruff |
| `make fill` | Create a fixture respondent with 24 random answers, so `/results` is reachable without clicking through the whole questionnaire |
| `make sh` | Open a shell inside the app container |

See `docs/spec.md` for the full scoring rules, data model, and page-by-page spec.
