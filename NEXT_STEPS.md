# VibeGraph Domain Learning Release Next Steps

## Current Branch

- Branch: `feature/domain-learning-layer-mvp`
- MVP commit: `cdba31a feat: add domain learning layer mvp`
- Follow-up workflow commit: `e0fe60f feat: expand domain learning workflows`
- Latest committed follow-up: `5ee6b8b feat: add learning filters and dashboard sections`
- Current follow-up scope adds non-destructive Learning Card archiving and release verification notes.
- Do not revert or edit unrelated worktree changes.

## Release Summary

The Domain Learning MVP turns AI review output into a lightweight learning backlog. When `domain_learning.learning_signals` are present in a `vibe report` or `vibe end` result, VibeGraph now saves Learning Cards, writes a session-level `learning_card.md`, and exposes cards through dashboard, growth, and CLI review surfaces.

The follow-up workflow commit makes those cards actionable after ingestion: users can view a specific card, mark it done, reopen it, add references, list all statuses, export markdown, and review summarized learning distribution.

The next local changes after `e0fe60f` add:

- `vibe learn add --domain <domain> --type <type> --title <title>` for manual Learning Card creation.
- `vibe learn list --domain ... --type ... --severity ... --search ...` for filtered review.
- `vibe learn list --limit 5` for focused terminal review.
- `vibe learn list --sort severity` for prioritized terminal review.
- `vibe learn list --due` for due-review terminal review.
- `vibe learn schedule <id> --date YYYY-MM-DD` for explicit review-date scheduling.
- `vibe learn list --all --json` for automation-friendly list export.
- Legacy `learnings.db` compatibility for `next_review_at`.
- Dashboard anchor sections: Summary, AI Review, Domain Learning, Sessions, Settings.
- Non-destructive archiving through `vibe learn archive <id>` and review through `vibe learn list --status archived`.
- JSON card output through `vibe learn show <id> --json` for automation and handoff scripts.
- Quick backlog stats through `vibe learn stats`.
- JSON backlog stats through `vibe learn stats --json`.
- Next-card review handoff through `vibe learn next` and `vibe learn next --json`.
- Release notes in `CHANGELOG.md`.

## Release Readiness Checklist

1. Re-run verification before release handoff.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m unittest discover -s tests -v`
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m py_compile vibe.py vibe_learning.py`
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m pip install -e .`
   - Access path: PowerShell or Windows Terminal > `where.exe vibe`
   - Access path: PowerShell or Windows Terminal > `vibe --help`

2. Review worktree state before committing release docs.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`
   - Expected files from this prep include code, tests, docs, `CHANGELOG.md`, and `NEXT_STEPS.md`.

3. Optional CLI smoke path for a fresh local data home.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph`
   - Set a temporary `VIBE_HOME`, run a small `vibe report` / `vibe end` fixture, then verify `vibe learn list`, `vibe learn list --limit 5`, `vibe learn list --sort severity`, `vibe learn list --due`, `vibe learn list --all --json`, `vibe learn show <id>`, `vibe learn show <id> --json`, `vibe learn next`, `vibe learn next --json`, `vibe learn schedule <id> --date 2026-07-01`, `vibe learn done <id>`, `vibe learn archive <id>`, `vibe learn list --status archived`, `vibe learn reopen <id>`, `vibe learn add-reference <id> --title "<title>" --url "<url>"`, `vibe learn stats`, `vibe learn stats --json`, and `vibe learn export`.

4. Prepare branch publication if requested.
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git log --oneline --decorate -n 5`
   - Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`
   - Do not run destructive git commands.

## User-Facing Command Access Paths

- Card list: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list`
- Include completed cards: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all`
- Filter cards: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all --domain Docker --type tool_gap --severity 4 --search logs`
- Limit cards: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --limit 5`
- Sort cards: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --sort severity`
- Due cards: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --due`
  - Output includes `next_review_at=YYYY-MM-DD` beside each due card.
- Schedule card: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn schedule <id> --date 2026-07-01`
- List JSON: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --all --json`
- Create manual card: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn add --domain Docker --type tool_gap --title "Docker log triage"`
- Latest card: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn card --last`
- Card detail: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn show <id>`
- Card detail JSON: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn show <id> --json`
- Next review card: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn next`
- Next review card JSON: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn next --json`
- Mark done: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn done <id>`
- Archive: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn archive <id>`
- Archived list: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --status archived`
- Reopen: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn reopen <id>`
- Add reference: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn add-reference <id> --title "<title>" --url "<url>"`
- Export markdown: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn export`
- Learning report: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn report`
- Learning stats: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn stats`
- Learning stats JSON: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn stats --json`
- Dashboard: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe dashboard`
- Growth report: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe growth`
- Claude Code slash path: Claude Code command box > `/vibe learn list`

## Known Environment Quirk

On this Windows workspace, `git status` can sometimes leave `.git/index.lock`. Before removing it, confirm no git process is running and only remove the specific lock file:

`C:\codex\app\vibegraph\.git\index.lock`

Safe lock recovery access path:

1. PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`
2. PowerShell or Windows Terminal > `Get-Process | Where-Object { $_.ProcessName -like '*git*' }`
3. If no git process is listed, PowerShell or Windows Terminal > `Remove-Item -LiteralPath 'C:\codex\app\vibegraph\.git\index.lock' -Force`
4. PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git status --short --branch`

Editable install verification can be blocked in the Codex sandbox if Python or pip selects a Windows temp folder that denies wheel/build-tracker writes, for example `C:\Users\seamo\AppData\Local\Temp`. In that case, record the failed command output, verify the CLI directly with a temporary `VIBE_HOME`, and rerun install verification outside the sandbox before publishing.

`install.bat` still needs a release-pass text update to advertise `vibe learn list` after install. This session did not edit it because the file is not currently UTF-8 readable by the patch tool; update it only after choosing and preserving the intended batch-file encoding.

Install-verification fallback smoke access path:

1. PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph`
2. PowerShell or Windows Terminal > `$env:VIBE_HOME='C:\Users\Public\Documents\ESTsoft\CreatorTemp\vibegraph-smoke'`
3. PowerShell or Windows Terminal > `python vibe.py learn add --domain Docker --type tool_gap --title "Docker smoke card" --severity 4`
4. PowerShell or Windows Terminal > `python vibe.py learn list --all --json`
5. PowerShell or Windows Terminal > `python vibe.py learn schedule <id> --date 2026-07-01`
6. PowerShell or Windows Terminal > `python vibe.py learn list --due`
