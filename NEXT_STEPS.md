# VibeGraph Domain Learning Next Steps

## Current Branch

- Branch: `feature/domain-learning-layer-mvp`
- Base MVP commit: `cdba31a feat: add domain learning layer mvp`
- Current follow-up work is in progress after that commit.
- Remote push has not been performed.

## Recommended Order

1. Learning Card lifecycle CLI
   - Add `vibe learn show <id>`.
   - Add `vibe learn done <id>`.
   - Add `vibe learn reopen <id>`.
   - Add `vibe learn add-reference <id> --title <title> --url <url>`.
   - Status: implemented locally, tests passing, not yet committed.

2. Growth and dashboard learning surfaces
   - Dashboard already has Domain Learning summary from the MVP.
   - Add Domain Learning summary to `growth.html`.
   - Status: implemented locally, focused test passing, not yet committed.

3. Documentation and slash command guidance
   - Sync `skills/vibe.md` from `vibe.py` `SKILL_CONTENT`.
   - Update README command table and access paths.
   - Update `사용법.txt` and `가이드.html`.
   - Status: implemented locally, not yet committed.

4. Verification and commit
   - Run `python -m unittest discover -s tests -v`.
   - Run `python -m py_compile vibe.py vibe_learning.py`.
   - Run temporary `VIBE_HOME` smoke tests for lifecycle commands.
   - Status: unittest and syntax `compile()` have passed once; `py_compile`, smoke tests, and commit still pending.

## Useful Access Paths

- Terminal card list: `vibe learn list`
- Terminal all cards: `vibe learn list --all`
- Terminal card detail: `vibe learn show <id>`
- Terminal mark done: `vibe learn done <id>`
- Terminal reopen: `vibe learn reopen <id>`
- Terminal add reference: `vibe learn add-reference <id> --title "<title>" --url "<url>"`
- Terminal export markdown: `vibe learn export`
- Claude Code slash path: `/vibe learn list`

## Context Handoff Notes

If this conversation becomes context-heavy, open a new conversation and give it:

1. This file: `C:\codex\app\vibegraph\NEXT_STEPS.md`
2. Current branch: `feature/domain-learning-layer-mvp`
3. Last known MVP commit: `cdba31a`
4. Instruction: continue from uncommitted follow-up work, run tests before committing.

## Known Environment Quirk

On this Windows workspace, `git status` sometimes leaves `.git/index.lock`.
Before removing it, confirm no git process is running and only remove:
`C:\codex\app\vibegraph\.git\index.lock`
