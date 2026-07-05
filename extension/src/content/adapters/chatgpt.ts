import { collectMessages, conversationFromMessages, fallbackMessages } from './common.js';
import type { CapturedConversation } from '../../core/types.js';

const CHATGPT_SELECTORS = [
  '[data-message-author-role]',
  'article',
  '[data-testid^="conversation-turn"]'
];

export function captureChatGpt(): CapturedConversation {
  const messages = collectMessages(CHATGPT_SELECTORS);
  return conversationFromMessages('chatgpt', messages.length > 0 ? messages : fallbackMessages());
}
