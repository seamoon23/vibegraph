import type { CaptureResponse } from '../core/types.js';

const SUPPORTED_HOSTS = new Set([
  'claude.ai',
  'chatgpt.com',
  'chat.openai.com',
  'gemini.google.com'
]);

chrome.sidePanel
  .setPanelBehavior({ openPanelOnActionClick: true })
  .catch((error) => console.error('Failed to enable VibeGraph side panel action click.', error));

function hostFromUrl(url?: string): string {
  if (!url) {
    return '';
  }

  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return '';
  }
}

async function activeTab(): Promise<ChromeApi.Tab | undefined> {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  return tabs[0];
}

async function sendCaptureMessage(tabId: number): Promise<CaptureResponse> {
  return chrome.tabs.sendMessage<CaptureResponse>(tabId, { type: 'VIBEGRAPH_CAPTURE' });
}

async function captureActiveTab(): Promise<CaptureResponse> {
  const tab = await activeTab();
  const host = hostFromUrl(tab?.url);

  if (!tab?.id || !SUPPORTED_HOSTS.has(host)) {
    return {
      ok: false,
      unsupported: true,
      reason: '현재 페이지는 아직 지원하지 않습니다. Claude, ChatGPT, Gemini 대화창에서 사용해 주세요.',
      title: tab?.title,
      url: tab?.url
    };
  }

  try {
    return await sendCaptureMessage(tab.id);
  } catch {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ['assets/content.js']
    });
    return sendCaptureMessage(tab.id);
  }
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!message || typeof message !== 'object') {
    return false;
  }

  if ((message as { type?: string }).type === 'VIBEGRAPH_CAPTURE_ACTIVE_TAB') {
    captureActiveTab()
      .then((response) => sendResponse(response))
      .catch((error) => {
        sendResponse({
          ok: false,
          reason: error instanceof Error ? error.message : '캡처 요청을 처리하지 못했습니다.'
        });
      });
    return true;
  }

  return false;
});
