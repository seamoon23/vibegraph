import type { VibeSession } from './types.js';

export function exportSessionJson(session: VibeSession): string {
  return JSON.stringify(session, null, 2);
}

export function exportAllSessionsJson(sessions: VibeSession[]): string {
  return JSON.stringify(
    {
      exportedAt: new Date().toISOString(),
      sessions
    },
    null,
    2
  );
}
