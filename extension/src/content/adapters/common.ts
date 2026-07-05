import type { CapturedConversation, MessageRole, SessionSource, VibeMessage } from '../../core/types.js';

type MessageCandidate = {
  role: MessageRole;
  text: string;
};

const ROLE_VALUES: MessageRole[] = ['user', 'assistant', 'system', 'unknown'];

function normalizeText(value: string): string {
  return value.replace(/\s+/g, ' ').trim();
}

function roleFromValue(value: string | null): MessageRole {
  const normalized = (value ?? '').toLowerCase();
  return ROLE_VALUES.find((role) => normalized.includes(role)) ?? 'unknown';
}

export function sourceFromLocation(location: Location): SessionSource {
  const host = location.hostname.toLowerCase();
  if (host === 'claude.ai') {
    return 'claude';
  }
  if (host === 'chatgpt.com' || host === 'chat.openai.com') {
    return 'chatgpt';
  }
  if (host === 'gemini.google.com') {
    return 'gemini';
  }
  return 'unknown';
}

export function cleanTitle(title: string, source: SessionSource): string {
  const suffixes: Record<SessionSource, string[]> = {
    claude: [' | Claude', ' - Claude'],
    chatgpt: [' | ChatGPT', ' - ChatGPT'],
    gemini: [' - Gemini', ' | Gemini'],
    manual: [],
    unknown: []
  };

  let next = title.trim();
  for (const suffix of suffixes[source]) {
    if (next.endsWith(suffix)) {
      next = next.slice(0, -suffix.length).trim();
    }
  }
  return next || 'Untitled conversation';
}

export function elementText(element: Element): string {
  const clone = element.cloneNode(true) as Element;
  clone.querySelectorAll('script, style, button, nav, aside, textarea, input').forEach((node) => node.remove());
  return normalizeText(clone.textContent ?? '');
}

export function roleForElement(element: Element): MessageRole {
  const roleAttribute =
    element.getAttribute('data-message-author-role') ??
    element.getAttribute('data-role') ??
    element.getAttribute('aria-label') ??
    element.closest('[data-message-author-role]')?.getAttribute('data-message-author-role') ??
    element.closest('[data-role]')?.getAttribute('data-role') ??
    element.closest('[aria-label]')?.getAttribute('aria-label') ??
    '';

  return roleFromValue(roleAttribute);
}

export function collectMessages(selectors: string[], fallbackRoot: ParentNode = document): VibeMessage[] {
  const candidates: MessageCandidate[] = [];
  const seen = new Set<string>();

  for (const selector of selectors) {
    fallbackRoot.querySelectorAll(selector).forEach((element) => {
      const text = elementText(element);
      if (text.length < 2 || seen.has(text)) {
        return;
      }

      seen.add(text);
      candidates.push({
        role: roleForElement(element),
        text
      });
    });
  }

  return candidates.map((candidate, index) => ({
    role: candidate.role,
    text: candidate.text,
    order: index + 1
  }));
}

export function fallbackMessages(): VibeMessage[] {
  const roots = ['main', '[role="main"]', 'body'];
  for (const selector of roots) {
    const root = document.querySelector(selector);
    if (!root) {
      continue;
    }

    const text = elementText(root);
    if (text.length >= 40) {
      return [{ role: 'unknown', text, order: 1 }];
    }
  }

  return [];
}

export function conversationFromMessages(
  source: SessionSource,
  messages: VibeMessage[]
): CapturedConversation {
  return {
    source,
    title: cleanTitle(document.title, source),
    url: location.href,
    capturedAt: new Date().toISOString(),
    messages
  };
}
