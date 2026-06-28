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

- Added manual Learning Card creation.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn add --domain Docker --type tool_gap --title "Docker log triage"`
- Added filtered Learning Card listing.
  - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all --domain Docker --type tool_gap --severity 4 --search logs`
- Added Dashboard 2nd-pass anchor sections for Summary, AI Review, Domain Learning, Sessions, and Settings.

### Safety Notes

- `vibe learn export` writes `LEARNINGS.generated.md` and does not overwrite a hand-written `LEARNINGS.md`.
- Dashboard and growth pages surface review candidates but keep Learning Card state changes in explicit CLI commands.
- The worktree may contain unrelated uncommitted non-doc edits; release documentation prep should not modify or revert them.

### Verification Commands

- Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m unittest discover -s tests -v`
- Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m py_compile vibe.py vibe_learning.py`
- Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`
