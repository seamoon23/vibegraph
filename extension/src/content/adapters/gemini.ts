import { collectMessages, conversationFromMessages, fallbackMessages } from './common.js';
import type { CapturedConversation } from '../../core/types.js';

const GEMINI_SELECTORS = [
  '[data-test-id="user-query"]',
  '[data-test-id="response"]',
  'user-query',
  'model-response',
  '.conversation-container [role="listitem"]',
  '.response-container'
];

export function captureGemini(): CapturedConversation {
  const messages = collectMessages(GEMINI_SELECTORS);
  return conversationFromMessages('gemini', messages.length > 0 ? messages : fallbackMessages());
}
