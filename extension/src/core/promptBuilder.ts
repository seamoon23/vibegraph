import { SCORE_KEYS, SCORE_LABELS, scoreTotal } from './scoring.js';
import type { VibeSession } from './types.js';

function scoreBlock(session: VibeSession): string {
  if (!session.scores) {
    return 'Scores: not evaluated yet';
  }

  const lines = SCORE_KEYS.map((key) => `- ${SCORE_LABELS[key]}: ${session.scores?.[key]} / 25`);
  return [...lines, `- Total: ${scoreTotal(session.scores)} / 100`].join('\n');
}

function conversationBlock(session: VibeSession): string {
  if (session.messages.length === 0) {
    return 'No messages were captured. Use the title, URL, and notes if available.';
  }

  return session.messages
    .map((message) => `[${message.order}] ${message.role}: ${message.text}`)
    .join('\n\n');
}

export function buildReportPrompt(session: VibeSession): string {
  return [
    'You are generating a VibeGraph report for one AI work session.',
    'Do not call external APIs. Use only the session data below.',
    'Score strictly. Normal work should usually land around 55-75 total. Reserve 85+ for unusually clean sessions.',
    'Return JSON only. Do not wrap it in Markdown and do not add explanation before or after it.',
    '',
    `Project: ${session.project || 'unspecified'}`,
    `Task: ${session.task || session.title || 'unspecified'}`,
    `Tags: ${session.tags.join(', ') || 'none'}`,
    `Source: ${session.source}`,
    `URL: ${session.url}`,
    `Captured At: ${session.capturedAt}`,
    '',
    'Manual scores from the user:',
    scoreBlock(session),
    '',
    'Notes:',
    session.notes?.trim() || 'none',
    '',
    'Captured conversation:',
    conversationBlock(session),
    '',
    'Return only valid JSON in this exact shape:',
    '{',
    '  "summary": "short session summary",',
    '  "scores": {',
    '    "oneShot": 0,',
    '    "context": 0,',
    '    "control": 0,',
    '    "clarity": 0',
    '  },',
    '  "promptSmells": [],',
    '  "goodExamples": [],',
    '  "badExamples": [],',
    '  "nextActions": []',
    '}'
  ].join('\n');
}

export function buildAllSessionsReportPrompt(sessions: VibeSession[]): string {
  const sessionBlocks = sessions.map((session, index) => {
    return [
      `## Session ${index + 1}`,
      `ID: ${session.id}`,
      `Project: ${session.project || 'unspecified'}`,
      `Task: ${session.task || session.title || 'unspecified'}`,
      `Source: ${session.source}`,
      `Captured At: ${session.capturedAt}`,
      scoreBlock(session),
      'Notes:',
      session.notes?.trim() || 'none',
      'Conversation excerpt:',
      conversationBlock({
        ...session,
        messages: session.messages.slice(0, 12)
      })
    ].join('\n');
  });

  return [
    'You are generating a VibeGraph portfolio report for multiple AI work sessions.',
    'Do not call external APIs. Use only the session data below.',
    'Return a concise Korean Markdown report with:',
    '- overall pattern',
    '- weakest axis',
    '- repeated prompt smells',
    '- 3 concrete next actions',
    '',
    ...sessionBlocks
  ].join('\n\n');
}
