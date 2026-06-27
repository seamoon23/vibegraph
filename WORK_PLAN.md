# Domain Learning Layer MVP Work Plan

## Defaults

- Work locally on `feature/domain-learning-layer-mvp`.
- Do not push to remote.
- Keep existing `vibe report`, `vibe end`, `vibe dashboard`, and `vibe growth` behavior compatible.
- Generate `LEARNINGS.generated.md` by default instead of overwriting `LEARNINGS.md`.
- Use SQLite from the Python standard library only.

## Implementation Order

1. Add tests for learning signal extraction, SQLite persistence, Markdown export, and empty legacy JSON handling.
2. Add `vibe_learning.py` for learning card normalization, DB storage, reports, and Markdown rendering.
3. Wire `vibe.py` so `vibe end` stores AI session summaries and ingests domain learning cards.
4. Add `vibe learn list`, `vibe learn card --last`, `vibe learn export`, and `vibe learn report`.
5. Add learning summary data to dashboard generation without removing the current session list.
6. Update prompt/docs/package metadata.
7. Run syntax and CLI verification with a temporary `VIBE_HOME`.

## Blocked Items Policy

If a decision is needed, record it in `NEXT_STEPS.md` and continue with independent work.
If a destructive or credential-dependent action is needed, record it in `BLOCKED.md` and stop only that action.
