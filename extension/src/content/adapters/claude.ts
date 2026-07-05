import { collectMessages, conversationFromMessages, fallbackMessages } from './common.js';
import type { CapturedConversation } from '../../core/types.js';

const CLAUDE_SELECTORS = [
  '[data-testid="user-message"]',
  '[data-testid="assistant-message"]',
  '[data-testid="conversation-turn"]',
  'main [class*="font-claude-message"]',
  'main [class*="message"]'
];

export function captureClaude(): CapturedConversation {
  const messages = collectMessages(CLAUDE_SELECTORS);
  return conversationFromMessages('claude', messages.length > 0 ? messages : fallbackMessages());
}
