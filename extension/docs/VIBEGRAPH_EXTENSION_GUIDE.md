# VibeGraph Chrome Extension Guide

## What It Is

VibeGraph Chrome Extension is a local-first companion for browser AI chats. It captures the current Claude, ChatGPT, or Gemini conversation only when you press the capture button, then lets you add project metadata, tags, four VibeGraph scores, notes, and exports.

It does not call a server or external AI API. Session data is stored in `chrome.storage.local` inside the browser profile.

## Local And Web Modes

- Local CLI mode is for project folders, files, tests, and Python-generated VibeGraph reports.
- Web extension mode is for browser conversations where the useful artifact is the chat itself.

The extension is independent from the existing Python CLI. It does not import, execute, or modify `vibe.py`.

## Install For Development

1. Access path: PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph\extension`
2. Access path: PowerShell or Windows Terminal > `npm install`
3. Access path: PowerShell or Windows Terminal > `npm run build`
4. Access path: Chrome address bar > `chrome://extensions`
5. Access path: Chrome extensions page > enable `Developer mode`
6. Access path: Chrome extensions page > `Load unpacked`
7. Select this folder: `C:\codex\app\vibegraph\extension\dist`

## Basic Use

1. Access path: Chrome > open `https://claude.ai`, `https://chatgpt.com`, `https://chat.openai.com`, or `https://gemini.google.com`.
2. Open a conversation you want to record.
3. Access path: Chrome toolbar > VibeGraph extension icon.
4. In the side panel, press `현재 대화 캡처`.
5. Add project, task, tags, notes, and four scores.
6. Use `리포트 프롬프트 복사`, `Markdown 저장`, `JSON 백업`, or `전체 백업 JSON`.

## Supported Sites

- `https://claude.ai/*`
- `https://chatgpt.com/*`
- `https://chat.openai.com/*`
- `https://gemini.google.com/*`

Unsupported pages show a friendly message and keep the side panel usable. You can still create a direct-input record with `직접 입력`.

## Stored Data

Stored session fields:

- Source site, title, URL, capture time
- Captured messages with role, text, and order
- Project, task, tags, notes, prompt smells
- Four VibeGraph scores

Access path: Chrome profile storage > extension `chrome.storage.local`.

## Limitations

- Conversation capture depends on each AI site's DOM. If a site changes markup, capture may return fewer messages or fail gracefully.
- The MVP does not sync across devices.
- The MVP does not call the Python CLI directly.
- The MVP does not watch pages in the background. It captures only after a user click.

## Troubleshooting

- If capture fails, refresh the AI chat page and retry with the conversation visible.
- If the side panel says the page is unsupported, move to Claude, ChatGPT, or Gemini.
- If the extension cannot load, rebuild with PowerShell or Windows Terminal > `cd C:\codex\app\vibegraph\extension` > `npm run build`, then reload it from Chrome > `chrome://extensions` > VibeGraph > reload.

## Future Pro Candidates

- Native Messaging bridge to the Python CLI
- Project-level growth charts
- Prompt smell classification
- Local backup reminders
- Multi-site comparison summaries
