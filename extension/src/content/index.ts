import { captureClaude } from './adapters/claude.js';
import { captureChatGpt } from './adapters/chatgpt.js';
import { captureGemini } from './adapters/gemini.js';
import { sourceFromLocation } from './adapters/common.js';
import type { CaptureResponse } from '../core/types.js';

function captureCurrentPage(): CaptureResponse {
  const source = sourceFromLocation(location);
  if (source === 'unknown') {
    return {
      ok: false,
      unsupported: true,
      reason: '현재 페이지는 아직 지원하지 않습니다. Claude, ChatGPT, Gemini 대화창에서 사용해 주세요.',
      title: document.title,
      url: location.href
    };
  }

  const conversation =
    source === 'claude'
      ? captureClaude()
      : source === 'chatgpt'
        ? captureChatGpt()
        : captureGemini();

  if (conversation.messages.length === 0) {
    return {
      ok: false,
      reason: '대화를 찾지 못했어요. 페이지를 새로고침하거나 대화가 보이는 상태에서 다시 시도해 주세요.',
      title: conversation.title,
      url: conversation.url
    };
  }

  return { ok: true, conversation };
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message || typeof message !== 'object' || (message as { type?: string }).type !== 'VIBEGRAPH_CAPTURE') {
    return false;
  }

  try {
    sendResponse(captureCurrentPage());
  } catch (error) {
    sendResponse({
      ok: false,
      reason: error instanceof Error ? error.message : '캡처 중 알 수 없는 오류가 발생했습니다.'
    });
  }

  return true;
});
