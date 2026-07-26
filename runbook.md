# Runbook: building disc-decode

Step-by-step path from an empty `apps/` folder to a working, CodeRabbit-clean
app. Written for the workflow in `CLAUDE.md`: everything runs in Docker, work
is split into small PRs, and every PR must pass tests, pass lint, and get a
clean CodeRabbit review before it merges into `main`.

The point of routing everything through PRs (instead of committing straight
to `main`) is that CodeRabbit only reviews pull requests — it has nothing to
say about a commit that lands directly on `main`. So "solve it with
CodeRabbit" means: never work on `main` directly, always open a PR, always
read what CodeRabbit says before merging.

---

## Phase 0 — One-time setup

Things you do once, before any feature work starts.

1. **Authenticate the GitHub CLI**, since later steps use it to open PRs and
   issues.
   ```
   gh auth login
   ```
2. **Install the CodeRabbit GitHub App on this repo.**
   - Go to https://github.com/marketplace/coderabbitai and install it.
   - When asked which repositories, select `thatpaulchang/disc-decode` (not
     "all repositories").
   - This is a one-time click-through in the browser; there's no CLI for it.
3. **Confirm it's active**: in the repo settings on GitHub, under
   *Integrations → Installed GitHub Apps*, CodeRabbit should be listed.
4. **Write the Docker setup**: `Dockerfile`, `docker-compose.yml` (or
   equivalent), and a `Makefile` with the targets CLAUDE.md promises —
   `make up`, `make test`, `make lint`, `make fmt`, `make fill`, `make sh`.
   This is infrastructure, not app logic, so it's fine to build and commit
   this part directly rather than treating it as its own reviewed phase —
   but everything after this point goes through a PR.
5. **Open the phase issues on GitHub** (one per phase below), so each PR in
   the phases that follow can reference "Closes #N" and there's an
   acceptance checklist to hold the work to. Use the spec's build order
   (`docs/spec.md`, bottom section) as the basis for what each issue covers.

Checkpoint: `make up` starts the container, `make sh` gets you a shell
inside it, and CodeRabbit shows up as an installed app on the repo.

---

## Phase 1 — Schema, questionnaire pages, saving answers

This is the spec's own Phase 1. Goal: a respondent can click through all 24
tetrads and answers land in SQLite.

1. **Branch**: `git checkout -b phase-1-schema-and-questions`
2. **Build**, inside Docker, in this order:
   - SQLite schema for `respondents`, `responses`, `results` (see
     `docs/spec.md` for exact columns and constraints — the CHECK
     constraints on style letters and tetrad range belong in the schema
     itself, not just app code).
   - Session cookie handling (Starlette `SessionMiddleware`) so a respondent
     gets a token on first visit.
   - `GET /q/<index>` and `POST /q/<index>` — render a tetrad, save an
     answer, validate before writing (index range, style letters, most ≠
     least).
   - The resume rule: any entry point sends the respondent to the first
     unanswered tetrad.
   - `make fill` — the dev helper that creates a respondent with 24 random
     valid answers.
3. **Test locally**: `make test` and `make lint` must both pass inside the
   container before you go further.
4. **Push and open the PR**: reference the Phase 1 issue with `Closes #N` in
   the PR description.
   ```
   git push -u origin phase-1-schema-and-questions
   gh pr create --fill
   ```
5. **Wait for CodeRabbit.** It comments on the PR automatically, usually
   within a couple of minutes — no need to trigger it manually. If you push
   more commits and want it to look again before it finishes on its own,
   comment `@coderabbitai review` on the PR.
6. **Work the findings**:
   - Read every comment CodeRabbit leaves.
   - Fix anything it flags as critical or major. That's a hard gate — see
     Definition of Done in `CLAUDE.md`.
   - For anything you disagree with, don't silently ignore it — reply on the
     comment explaining why (e.g. "intentional, see spec.md line X"), or
     ask me if you're not sure it's a false positive.
   - Push fixes to the same branch; CodeRabbit re-reviews automatically.
7. **Also confirm by hand**: click through all 24 tetrads in a browser at a
   phone-sized window, refresh mid-way to check progress survives, go back
   and change an earlier answer to check it updates rather than duplicates.
   CodeRabbit reviews code, not behavior — this step is still on you.
8. **Merge** once tests pass, lint passes, CodeRabbit has no open
   critical/major findings, and the phone-window check above works.
   ```
   gh pr merge --squash
   ```

---

## Phase 2 — Scoring and the results page

1. **Branch**: `git checkout -b phase-2-scoring-and-results`
2. **Build**:
   - Scoring as a pure function in `apps/logic/` (no database access), so it
     can be unit tested directly — per the Conventions section of
     `CLAUDE.md`.
   - Server-side trigger: scoring runs once, when the 24th tetrad is
     answered. Never in the browser.
   - `results` table writes: `most_`, `least_`, `diff_` per style,
     `top_styles`/`bottom_styles` as sets (ties, including all-four-tied,
     stay as sets — never collapsed to one pick).
   - `GET /results` — redirects to the first unanswered tetrad if the
     respondent isn't done yet; otherwise renders the four diff scores, top
     and bottom styles, the style descriptions from `items.py`, the
     ipsative-scoring note, and the required disclaimer.
3. **Tests before anything else counts as done**:
   - Hand-checked fixture: write 24 answers out on paper yourself, work out
     the expected `most`/`least`/`diff` by hand, assert the function
     produces those exact numbers. Do not generate the expected values by
     running the scoring function — that only proves the function agrees
     with itself.
   - Property test: for any valid set of 24 answers, the four `diff` values
     sum to zero.
   - Tie-handling test, including the case where all four styles tie.
   - `validate_content()` from `items.py`, run as a test.
4. **`make test` and `make lint`** pass inside Docker.
5. **PR, CodeRabbit, fix, re-review** — same loop as Phase 1, steps 4–6.
6. **By-hand check**: reach `/results` via `make fill`, confirm the numbers
   on screen match what the fixture test expects, confirm the disclaimer
   text is present and matches `docs/spec.md` near-verbatim.
7. **Merge** once tests, lint, CodeRabbit, and the by-hand check all pass.

---

## Phase 3 — Landing page, past results, README, mobile pass

1. **Branch**: `git checkout -b phase-3-landing-and-polish`
2. **Build**:
   - `/` — explains what the app is, carries the disclaimer, takes a display
     name, starts a run.
   - `/health` — returns `{"status": "ok"}`.
   - Whatever "past results" means for a single-respondent app per the spec
     (re-check `docs/spec.md` — if it's silent on this, stop and ask rather
     than inventing an account system; CLAUDE.md is explicit that this app
     has no accounts).
   - README: real setup instructions (`make up`, etc.) plus the required
     disclaimer text.
   - Mobile pass: tap targets ≥44px, one tetrad fits a phone screen without
     scrolling, real `<label>` elements on every radio, visible focus
     outlines, styles labeled by letter and name (not color alone).
3. **`make test` and `make lint`** pass inside Docker.
4. **PR, CodeRabbit, fix, re-review** — same loop as before.
5. **By-hand check on an actual phone-sized browser window**: landing page →
   full questionnaire → results, nothing scrolls or clips, disclaimer is
   present on landing and results pages.
6. **Merge** once everything above is green.

---

## Standing loop for every PR, every phase

This is the part that repeats. Once Phase 0 is done, every unit of work —
whether it's a full phase above or a smaller fix later — follows the same
six steps:

1. Branch off `main`.
2. Build and test inside Docker (`make test`, `make lint`) — never run
   `python`, `pip`, or `uvicorn` on the host machine.
3. Push, open a PR with `gh pr create`, link the relevant issue.
4. Let CodeRabbit review automatically; re-request with
   `@coderabbitai review` if you push new commits and want a fresh pass
   before it finishes on its own.
5. Fix every critical/major finding; reply on anything you skip and say why.
6. Merge only when tests pass, lint passes, CodeRabbit is clean, and you've
   confirmed the behavior by hand in a browser.

If at any point the spec (`docs/spec.md`) doesn't say what to do, stop and
ask — don't invent scoring behavior, validation rules, or scope beyond what
`CLAUDE.md` already rules out (no teams, guessing, timers, multiplayer,
accounts, or admin views).