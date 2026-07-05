# VibeGraph Extension Architecture

## Overview

```text
Chrome action
  -> background service worker
      -> opens side panel
      -> asks active tab content script to capture
          -> site adapter extracts visible conversation
      -> side panel stores and edits local session
          -> chrome.storage.local
          -> Markdown / JSON / prompt export
```

## Main Parts

- `manifest.json`: Manifest V3 permissions, side panel path, supported hosts, and content script registration.
- `src/background/serviceWorker.ts`: Opens the side panel and coordinates active-tab capture.
- `src/content/index.ts`: Receives capture requests and delegates to the active site adapter.
- `src/content/adapters/`: Best-effort DOM extraction for Claude, ChatGPT, Gemini, plus shared helpers.
- `src/sidepanel/`: Local UI for capture, session editing, scoring, and export.
- `src/core/`: Shared types, scoring, prompt generation, Markdown/JSON export, date helpers, and storage.

## Data Flow

1. User presses the Chrome toolbar extension icon.
2. The service worker opens `src/sidepanel/index.html`.
3. User presses `현재 대화 캡처`.
4. The side panel sends `VIBEGRAPH_CAPTURE_ACTIVE_TAB` to the service worker.
5. The service worker checks the active tab host.
6. Supported tabs receive `VIBEGRAPH_CAPTURE`.
7. The content script returns a `CapturedConversation`.
8. The side panel creates a `VibeSession` and saves it in `chrome.storage.local`.

## Session Shape

```ts
export type SessionSource = 'claude' | 'chatgpt' | 'gemini' | 'unknown';
export type MessageRole = 'user' | 'assistant' | 'system' | 'unknown';

export interface VibeSession {
  id: string;
  source: SessionSource;
  title: string;
  url: string;
  project: string;
  task: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  capturedAt: string;
  messages: VibeMessage[];
  scores?: VibeScores;
  notes?: string;
  promptSmells?: string[];
}
```

## Adapter Strategy

Adapters are intentionally defensive:

- Try several selectors per site.
- Remove buttons, inputs, scripts, and navigation before reading text.
- Deduplicate repeated message text.
- Fall back to visible `main` or `body` text if selectors fail.
- Return a friendly failure state when no usable text is found.

This keeps DOM changes from crashing the whole extension.

## Privacy And Security

- No server endpoint is configured.
- No external AI API is called.
- Capture runs only after a user action.
- Data stays in browser-local storage unless the user exports Markdown or JSON.
- Host permissions are limited to Claude, ChatGPT, and Gemini.

## Build Output

Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph\extension` > `npm run build`

The build writes loadable extension files to:

```text
C:\codex\app\vibegraph\extension\dist
```

`scripts/copy-manifest.mjs` copies the source `manifest.json` into `dist/manifest.json` after Vite finishes.

## Future CLI Bridge

A future Native Messaging bridge can connect the extension to the existing Python CLI without changing the MVP storage contract:

```text
Side panel
  -> Native Messaging host
      -> vibe.py report/end-compatible JSON
          -> existing VibeGraph report flow
```

That bridge should stay optional so the extension remains usable as a browser-only local tool.
