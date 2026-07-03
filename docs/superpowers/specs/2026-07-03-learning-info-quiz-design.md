# Learning Info Cards and Quiz MVP Design

## Goal

Help users review domain gaps immediately after AI-assisted work without adding scoring, accounts, or a new persistence model. The first version surfaces 3-5 existing Learning Cards as short info cards and a self-check quiz.

## Scope

- Show richer Domain Learning info cards in dashboard and growth views.
- Add a terminal quiz view that reuses the same next-review candidates.
- Do not store quiz answers, scores, attempts, or history.
- Do not generate new factual claims beyond existing card fields.

## Data Source

Use existing Learning Card fields:

- `domain`
- `type`
- `title`
- `evidence`
- `micro_summary`
- `micro_goal`
- `self_checkpoints`
- `severity`
- `next_review_at`

Candidate order follows the existing `learning_summary().review_candidates` / `vibe learn next` priority:

1. Due open cards first.
2. Highest-severity open cards as fallback.
3. Maximum 5 cards.

## Dashboard and Growth Info Cards

Each card should display:

- Domain/type/severity.
- Title.
- One-line summary, using `micro_summary`, then `evidence`, then title fallback.
- Five-minute goal, using `micro_goal` fallback text when missing.
- One or two self-check questions from `self_checkpoints`; if empty, show a generic self-explain prompt.
- Access command such as `vibe learn show <id>`.

## CLI Quiz

Add:

`vibe learn quiz [--limit N] [--as-of YYYY-MM-DD] [--json]`

Text mode prints numbered quiz cards with:

- Card id, domain, severity, title.
- Question prompts from self-checkpoints.
- Five-minute goal.
- Access path for `vibe learn show <id>`.

JSON mode returns the same quiz cards for automation.

## Error Handling

- `--limit` must be a positive integer.
- `--as-of` must be `YYYY-MM-DD`.
- If there are no cards, print a short empty-state message and the access path for creating/listing cards.

## Testing

- CLI test for `vibe learn quiz`.
- CLI test for `vibe learn quiz --json`.
- Dashboard test should assert info-card text and self-check prompt are rendered.
- Growth test should assert info-card text and `vibe learn quiz` access path are rendered.
