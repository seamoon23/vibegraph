import type { ExtensionSettings, VibeSession } from './types.js';

const SESSIONS_KEY = 'vibegraph.sessions';
const SETTINGS_KEY = 'vibegraph.settings';

const DEFAULT_SETTINGS: ExtensionSettings = {
  onboardingDismissed: false,
  privacyNoticeCollapsed: true
};

function sortSessions(sessions: VibeSession[]): VibeSession[] {
  return [...sessions].sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export async function loadSessions(): Promise<VibeSession[]> {
  const result = await chrome.storage.local.get(SESSIONS_KEY);
  const sessions = result[SESSIONS_KEY];
  return Array.isArray(sessions) ? sortSessions(sessions as VibeSession[]) : [];
}

export async function saveSessions(sessions: VibeSession[]): Promise<void> {
  await chrome.storage.local.set({ [SESSIONS_KEY]: sortSessions(sessions) });
}

export async function saveSession(session: VibeSession): Promise<VibeSession[]> {
  const sessions = await loadSessions();
  const next = sortSessions([
    session,
    ...sessions.filter((candidate) => candidate.id !== session.id)
  ]);
  await saveSessions(next);
  return next;
}

export async function deleteSession(sessionId: string): Promise<VibeSession[]> {
  const sessions = (await loadSessions()).filter((session) => session.id !== sessionId);
  await saveSessions(sessions);
  return sessions;
}

export async function loadSettings(): Promise<ExtensionSettings> {
  const result = await chrome.storage.local.get(SETTINGS_KEY);
  return {
    ...DEFAULT_SETTINGS,
    ...((result[SETTINGS_KEY] as Partial<ExtensionSettings> | undefined) ?? {})
  };
}

export async function saveSettings(settings: ExtensionSettings): Promise<void> {
  await chrome.storage.local.set({ [SETTINGS_KEY]: settings });
}
