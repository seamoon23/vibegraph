# VibeGraph Domain Learning Release Handoff

## Current Branch

- Branch: `feature/domain-learning-layer-mvp`
- Scope: Domain Learning Card MVP follow-up workflows, review handoff, deterministic review-date checks, CLI validation, and release docs.
- Latest commit access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git log --oneline -n 1`

## Recent Baseline Commits

- `503173f docs: add domain learning release handoff`
- `aa82b52 fix: validate learning cli inputs`
- `52c9270 fix: validate learning review dates`
- `d0ca8e6 feat: add deterministic learning review dates`
- `1131794 feat: align learning review candidates`
- `4ba0430 feat: extend learning card review workflows`
- `5ee6b8b feat: add learning filters and dashboard sections`

## Verification Access Paths

- Full tests: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -m unittest discover -s tests -v`
- Syntax check: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `python -c "from pathlib import Path; [compile(Path(p).read_text(encoding='utf-8'), p, 'exec') for p in ('vibe.py','vibe_learning.py')]; print('syntax ok')"`
- Whitespace check: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `git diff --check`

## User-Facing Smoke Paths

- List due cards as of a fixed date: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --due --as-of 2026-07-01`
- Next review card JSON as of a fixed date: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn next --as-of 2026-07-01 --json`
- Self-check quiz JSON: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn quiz --limit 3 --json`
- Learning stats JSON: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn stats --json`
- Archived list: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph` > `vibe learn list --status archived`

## Known Blocker

- `install.bat` still needs a release-pass success-screen text update to mention `vibe learn list`.
- This file is not currently UTF-8 readable by the patch tool, so preserve its intended batch-file encoding before editing.

## Git Lock Note

On this Windows workspace, read-only git commands can recreate a zero-byte `.git/index.lock`. Before removing it, confirm no git process is running:

1. PowerShell or Windows Terminal > `Get-Process | Where-Object { $_.ProcessName -like '*git*' }`
2. If no git process is active, remove only `C:\codex\app\vibegraph\.git\index.lock`.
