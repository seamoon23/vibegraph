# Changelog

All notable release-prep notes for this branch are collected here.

## 0.4.0 - Domain Learning MVP - 2026-06-28

Branch: `feature/domain-learning-layer-mvp`

### Added

- Added the Domain Learning layer MVP in `cdba31a feat: add domain learning layer mvp`.
- Persisted AI session summaries to `ai_sessions.db` and Domain Learning Cards to `learnings.db`.
- Added Learning Card extraction from `domain_learning.learning_signals` during `vibe report` / `vibe end` flows.
- Added per-session `learning_card.md` output when a report contains learning signals.
- Added terminal learning commands:
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn card --last`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn export`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn report`
- Added Domain Learning summary panels to `vibe dashboard`.
- Added package metadata for the `vibe_learning` module.

### Expanded

- Expanded the Domain Learning workflow in `e0fe60f feat: expand domain learning workflows`.
- Added lifecycle commands for Learning Cards:
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn show <id>`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn done <id>`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn reopen <id>`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn add-reference <id> --title "<title>" --url "<url>"`
- Added `--all` listing support so completed cards can be reviewed after being marked done.
- Added reference-link storage and rendering for Learning Cards.
- Added Domain Learning summary panels to `vibe growth`.
- Updated Claude Code slash command guidance for `/vibe learn ...` workflows.
- Updated Korean user-facing guide files with learning command access paths.

### In Progress After `e0fe60f`

- Committed manual Learning Card creation, list filters, and Dashboard 2nd-pass sections in `5ee6b8b feat: add learning filters and dashboard sections`.
- Added manual Learning Card creation.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn add --domain Docker --type tool_gap --title "Docker log triage"`
- Added filtered Learning Card listing.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all --domain Docker --type tool_gap --severity 4 --search logs`
- Added limited Learning Card listing.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --limit 5`
- Added sorted Learning Card listing.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --sort severity`
- Added due-review Learning Card listing.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --due`
- Added Learning Card review-date scheduling.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn schedule <id> --date 2026-07-01`
- Added JSON Learning Card list output.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all --json`
- Added a legacy `learnings.db` guard that adds `next_review_at` when older databases do not have the column.
- `vibe learn list --due` now prints `next_review_at=YYYY-MM-DD` with each due card.
- Added Dashboard 2nd-pass anchor sections for Summary, AI Review, Domain Learning, Sessions, and Settings.
- Added non-destructive Learning Card archiving.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn archive <id>`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --status archived`
- Added JSON Learning Card output for automation.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn show <id> --json`
- Added quick Learning Card stats.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn stats`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn stats --json`
- Added next-card selection for review handoff.
  - Due open cards are selected first, then highest-severity open cards.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn next`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn next --json`
- Added deterministic review-date checks for automation.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --due --as-of 2026-07-01`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn next --as-of 2026-07-01 --json`
  - Invalid `--as-of` values now fail fast unless they use `YYYY-MM-DD`.
- Added lightweight Domain Learning info cards and self-check quiz output without score/history persistence.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn quiz --limit 3`
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn quiz --limit 3 --json`
- Invalid `vibe learn list --limit` values now fail fast unless they are positive integers.
- Invalid `vibe learn list --severity` and `vibe learn add --severity` values now fail fast unless they are in `1-5`.
- Aligned dashboard and growth review candidates with the same due-first priority as `vibe learn next`.
- Hardened legacy `learnings.db` migration so old rows expose blank `next_review_at` values and can still be listed, shown, and scheduled.

### Safety Notes

- `vibe learn export` writes `LEARNINGS.generated.md` and does not overwrite a hand-written `LEARNINGS.md`.
- Dashboard and growth pages surface review candidates but keep Learning Card state changes in explicit CLI commands.
- The worktree may contain unrelated uncommitted non-doc edits; release documentation prep should not modify or revert them.

### Verification Commands

- Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m unittest discover -s tests -v`
- Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m py_compile vibe.py vibe_learning.py`
- Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m pip install -e .`
- Access path: PowerShell or Windows Terminal > `where.exe vibe` > `vibe --help`
- Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`
