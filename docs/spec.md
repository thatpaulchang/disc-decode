# DISC Questionnaire — Spec

*Save as `docs/spec.md`. This is the source of truth. If something here is unclear or missing, ask — don't invent it.*

## What it does

One person opens the app, enters a display name, answers 24 forced-choice questions, and sees their DISC profile. Answers and results are stored in SQLite. 

## The questionnaire

24 tetrads. Each tetrad shows 4 statements — one each for D, I, S, and C — and the respondent picks:

- one statement as **most like me**
- a different statement as **least like me**

The content lives in `app/logic/items.py` as a constant. Do not move it to the database and do not rewrite the statements; they're original text chosen for balance, and replacing them with items from a published instrument would be a copyright problem.

One tetrad per page. Answers save as the respondent goes, so a refresh or a closed laptop doesn't lose progress.

## Scoring

This is **ipsative** (forced-choice) scoring: results rank a person's four styles against each other, not against a norm group. Say so on the results page.

For each style:

| Score | How |
|---|---|
| `most_<style>` | count of tetrads where that style's statement was picked as *most* |
| `least_<style>` | count where it was picked as *least* |
| `diff_<style>` | `most_<style> − least_<style>` |

- `most` values sum to 24. `least` values sum to 24. **`diff` values always sum to zero.**
- `top_styles` = every style tied for the highest `diff`. `bottom_styles` = every style tied for the lowest.
- Both are stored as sets, never collapsed to a single arbitrary pick.
- All four tied is legal. Both sets then contain all four. Don't special-case it.

Scoring runs server-side, once, when the last tetrad is answered. Never in the browser.

## Data (SQLite)

| Table | Columns |
|---|---|
| `respondents` | id, token, display_name, created_at |
| `responses` | respondent_id, tetrad_index, most_style, least_style — unique per (respondent_id, tetrad_index) |
| `results` | respondent_id (unique), most_d/i/s/c, least_d/i/s/c, diff_d/i/s/c, top_styles, bottom_styles, completed_at |

`token` is a random value held in the signed session cookie — it's how the server knows who's answering. A respondent can only read and write their own rows.

Constraints worth putting in the schema, not just the application code:
- `most_style` and `least_style` each restricted to `D`, `I`, `S`, `C`
- `most_style <> least_style`
- `tetrad_index` between 0 and 23

Database file path comes from the `DB_PATH` environment variable.

## Validation

Reject, with a clear message and no database write:

- a tetrad index outside 0–23
- a style letter that isn't one of D, I, S, C
- most and least being the same statement
- answering a tetrad that's already answered — treat as an update, not a duplicate
- any request whose session token doesn't match an existing respondent

## Pages

| Page | Does |
|---|---|
| `/` | Explains what this is, carries the disclaimer, takes a display name, starts a run |
| `/q/<index>` | One tetrad. Radio buttons for most and least. Back and next. |
| `/results` | The four diff scores, top and bottom styles, style descriptions, ipsative note, disclaimer. Also links to review/change an answer, and to retake from scratch. |
| `POST /retake` | Deletes the respondent's answers and results (same session/token), then sends them to `/q/0` to start over |
| `/health` | Returns `{"status": "ok"}` for the container |

Resume rule: starting or returning sends the respondent to the **first unanswered tetrad**. If all 24 are answered, to `/results`.

Reviewing after completion: a respondent who has finished can still open any `/q/<index>` to see or change that answer — scoring recomputes from current answers on every `/results` visit, so an edit is reflected the next time results are viewed. Advancing past a reviewed question goes to the next question in order (or `/results` after the last one), not back to "first unanswered" — there isn't one once everything's answered.

## Cases to handle and test

1. Refresh mid-questionnaire → resumes at the first unanswered tetrad, keeps prior answers.
2. Going back and changing an earlier answer → updates that row, doesn't create a second.
3. Same statement picked for most and least → rejected before any write.
4. Direct URL to `/q/50` or `/q/-1` → clean error, no write.
5. `/results` before finishing → redirect to the first unanswered tetrad.
6. All four styles tied → both sets hold all four, results page renders, nothing crashes.
7. No session cookie → treated as a new visitor, not an error.
8. Reviewing an early question after finishing, then clicking Next → goes to the next question in order, not straight to `/results`.
9. Retake after finishing → answers and results are cleared, respondent restarts at question 1 with the same session.

## Tests that matter

- **Hand-checked fixtures.** Write out a set of 24 answers on paper, work out the expected scores yourself, assert against those numbers. Do not generate the expected values with the scoring function — that proves nothing.
- **The sum-to-zero invariant.** For any valid set of answers, the four `diff` values sum to zero. Good property test.
- **`validate_content()`** from `items.py`, run as a test — catches hand-editing mistakes in the tetrads.
- **Tie behavior**, including the all-four-tied case.

## Development helper

`make fill` creates a respondent with 24 random valid answers, so the results page can be reached without clicking through the whole thing. You'll use this constantly.

## Non-functional

- **Mobile first.** Tap targets at least 44px; one tetrad fits on a phone screen without scrolling.
- **Accessible.** Real `<label>` elements on every radio, visible focus outlines, readable contrast, styles identified by letter and name rather than colour alone.
- **Private.** Results are personal data. Use made-up names for demos. There's no reason to retain anything.

## Required disclaimer

This text goes in the README, on the landing page, and on the results page, near enough verbatim:

> This is an unvalidated, for-entertainment questionnaire inspired by the public-domain DISC model first described by William Moulton Marston in *Emotions of Normal People* (1928). It has no validity evidence behind it and is not suitable for hiring, promotion, or performance decisions. Scores are ipsative — they rank your four styles against each other, not against other people. All questionnaire text is original to this project. "DiSC®" and "Everything DiSC®" are registered trademarks of John Wiley & Sons, Inc., which has no connection to this project.

## Build order

1. Schema, questionnaire pages, saving answers.
2. Scoring and the results page.
3. Landing page, past results, README, mobile pass.