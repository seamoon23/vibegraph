import {
  clampScore,
  isCompleteScoreSet,
  scoreTotal
} from './scoring.js';
import { exportSessionJson } from './exportJson.js';
import { exportSessionMarkdown } from './exportMarkdown.js';
import { buildReportPrompt } from './promptBuilder.js';
import type { VibeSession } from './types.js';

type TestCase = {
  name: string;
  run: () => void;
};

function assertEqual<T>(actual: T, expected: T, message: string): void {
  if (actual !== expected) {
    throw new Error(`${message}. Expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assertIncludes(actual: string, expected: string, message: string): void {
  if (!actual.includes(expected)) {
    throw new Error(`${message}. Missing ${JSON.stringify(expected)} in ${JSON.stringify(actual)}`);
  }
}

const session: VibeSession = {
  id: 'session-1',
  source: 'claude',
  title: 'Chrome Extension MVP',
  url: 'https://claude.ai/chat/abc',
  project: 'vibegraph',
  task: 'Chrome Extension MVP',
  tags: ['chrome', 'mvp'],
  createdAt: '2026-07-04T00:00:00.000Z',
  updatedAt: '2026-07-04T00:01:00.000Z',
  capturedAt: '2026-07-04T00:01:00.000Z',
  messages: [
    { role: 'user', text: 'Build a local-first extension.', order: 1 },
    { role: 'assistant', text: 'Here is a plan.', order: 2 }
  ],
  scores: {
    oneShot: 20,
    context: 21,
    control: 18,
    clarity: 22
  },
  notes: 'Keep CLI untouched.',
  promptSmells: ['scope drift']
};

const tests: TestCase[] = [
  {
    name: 'clampScore keeps scores inside the 0-25 range',
    run: () => {
      assertEqual(clampScore(-1), 0, 'negative scores clamp to zero');
      assertEqual(clampScore(26), 25, 'scores above 25 clamp to 25');
      assertEqual(clampScore(12.8), 13, 'decimal scores round to nearest integer');
      assertEqual(clampScore(Number.NaN), 0, 'NaN scores become zero');
    }
  },
  {
    name: 'scoreTotal adds four complete axes',
    run: () => {
      assertEqual(scoreTotal(session.scores), 81, 'score total');
      assertEqual(isCompleteScoreSet(session.scores), true, 'score set completeness');
      assertEqual(isCompleteScoreSet(undefined), false, 'missing score set completeness');
    }
  },
  {
    name: 'exportSessionMarkdown contains user-facing report sections',
    run: () => {
      const markdown = exportSessionMarkdown(session);
      assertIncludes(markdown, '# VibeGraph Session', 'markdown title');
      assertIncludes(markdown, '## Basic Info', 'basic info section');
      assertIncludes(markdown, '## Scores', 'scores section');
      assertIncludes(markdown, 'Total: 81 / 100', 'score total');
      assertIncludes(markdown, 'Build a local-first extension.', 'captured message');
    }
  },
  {
    name: 'exportSessionJson serializes stable session data',
    run: () => {
      const payload = JSON.parse(exportSessionJson(session)) as VibeSession;
      assertEqual(payload.id, 'session-1', 'json id');
      assertEqual(payload.messages.length, 2, 'json message count');
      assertEqual(payload.scores?.clarity, 22, 'json scores');
    }
  },
  {
    name: 'buildReportPrompt asks for the existing VibeGraph JSON result shape',
    run: () => {
      const prompt = buildReportPrompt(session);
      assertIncludes(prompt, 'Project: vibegraph', 'project line');
      assertIncludes(prompt, 'Chrome Extension MVP', 'task line');
      assertIncludes(prompt, '"summary"', 'summary json key');
      assertIncludes(prompt, '"scores"', 'scores json key');
      assertIncludes(prompt, '"promptSmells"', 'prompt smells json key');
      assertIncludes(prompt, 'Do not call external APIs', 'privacy instruction');
    }
  }
];

for (const test of tests) {
  test.run();
  console.log(`ok - ${test.name}`);
}
