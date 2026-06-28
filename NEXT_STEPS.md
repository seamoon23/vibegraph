# VibeGraph Domain Learning Release Next Steps

## Current Branch

- Branch: `feature/domain-learning-layer-mvp`
- MVP commit: `cdba31a feat: add domain learning layer mvp`
- Follow-up workflow commit: `e0fe60f feat: expand domain learning workflows`
- Current follow-up scope also includes manual Learning Card creation, list filters, and Dashboard 2nd-pass sections.
- Do not revert or edit unrelated worktree changes.

## Release Summary

The Domain Learning MVP turns AI review output into a lightweight learning backlog. When `domain_learning.learning_signals` are present in a `vibe report` or `vibe end` result, VibeGraph now saves Learning Cards, writes a session-level `learning_card.md`, and exposes cards through dashboard, growth, and CLI review surfaces.

The follow-up workflow commit makes those cards actionable after ingestion: users can view a specific card, mark it done, reopen it, add references, list all statuses, export markdown, and review summarized learning distribution.

The next local changes after `e0fe60f` add:

- `vibe learn add --domain <domain> --type <type> --title <title>` for manual Learning Card creation.
- `vibe learn list --domain ... --type ... --severity ... --search ...` for filtered review.
- Dashboard anchor sections: Summary, AI Review, Domain Learning, Sessions, Settings.
- Release notes in `CHANGELOG.md`.

## Release Readiness Checklist

1. Re-run verification before release handoff.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m unittest discover -s tests -v`
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m py_compile vibe.py vibe_learning.py`

2. Review worktree state before committing release docs.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`
   - Expected files from this prep include code, tests, docs, `CHANGELOG.md`, and `NEXT_STEPS.md`.

3. Optional CLI smoke path for a fresh local data home.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph`
   - Set a temporary `VIBE_HOME`, run a small `vibe report` / `vibe end` fixture, then verify `vibe learn list`, `vibe learn show <id>`, `vibe learn done <id>`, `vibe learn reopen <id>`, `vibe learn add-reference <id> --title "<title>" --url "<url>"`, and `vibe learn export`.

4. Prepare branch publication if requested.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git log --oneline --decorate -n 5`
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`
   - Do not run destructive git commands.

## User-Facing Command Access Paths

- Card list: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list`
- Include completed cards: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all`
- Filter cards: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all --domain Docker --type tool_gap --severity 4 --search logs`
- Create manual card: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn add --domain Docker --type tool_gap --title "Docker log triage"`
- Latest card: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn card --last`
- Card detail: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn show <id>`
- Mark done: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn done <id>`
- Reopen: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn reopen <id>`
- Add reference: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn add-reference <id> --title "<title>" --url "<url>"`
- Export markdown: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn export`
- Learning report: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn report`
- Dashboard: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe dashboard`
- Growth report: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe growth`
- Claude Code slash path: Claude Code command box > `/vibe learn list`

## Known Environment Quirk

On this Windows workspace, `git status` can sometimes leave `.git/index.lock`. Before removing it, confirm no git process is running and only remove the specific lock file:

`C:\codex\app\vibegraph\.git\index.lock`
