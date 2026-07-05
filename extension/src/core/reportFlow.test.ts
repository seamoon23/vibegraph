import { buildLocalReportDraft } from './autoReport.js';
import { parseAiReportResult } from './aiResult.js';
import { buildLocalOverallReport } from './overallReport.js';
import type { VibeSession } from './types.js';

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
  title: 'Extension UX',
  url: 'https://claude.ai/chat/abc',
  project: 'vibegraph',
  task: 'Extension UX',
  tags: ['chrome'],
  createdAt: '2026-07-05T00:00:00.000Z',
  updatedAt: '2026-07-05T00:00:00.000Z',
  capturedAt: '2026-07-05T00:00:00.000Z',
  messages: [
    {
      role: 'user',
      order: 1,
      text: 'extension/src/sidepanel/App.ts를 수정해줘. 저장은 버튼을 눌렀을 때만 하고 npm run typecheck로 검증해줘.'
    },
    { role: 'assistant', order: 2, text: '수정하겠습니다.' },
    { role: 'user', order: 3, text: '아니, 삭제 버튼 위치도 다시 수정해줘.' }
  ]
};

const draft = buildLocalReportDraft(session);
assertIncludes(draft.summary, '무료 초안 채점', 'local draft explains that scoring is a draft');
assertEqual(draft.scores.clarity > 0, true, 'local draft produces clarity score');
assertEqual(draft.nextActions.length > 0, true, 'local draft produces next actions');

const unknownRoleDraftA = buildLocalReportDraft({
  ...session,
  id: 'unknown-a',
  messages: [{ role: 'unknown', order: 1, text: '수동로드까지는 되었는데 클릭해도 아무 작동이 없습니다. 콘솔에도 오류가 없습니다.' }]
});
const unknownRoleDraftB = buildLocalReportDraft({
  ...session,
  id: 'unknown-b',
  messages: [{ role: 'unknown', order: 1, text: 'AGENTS.md를 읽고 extension/src/sidepanel/App.ts 저장 버튼과 npm run build 검증을 처리해줘.' }]
});
assertEqual(
  JSON.stringify(unknownRoleDraftA.scores) === JSON.stringify(unknownRoleDraftB.scores),
  false,
  'local draft scores should vary for unknown-role captures'
);

const overall = buildLocalOverallReport([
  {
    ...session,
    scores: { oneShot: 18, context: 16, control: 14, clarity: 20 },
    promptSmells: ['범위 기준이 늦게 정리됨']
  },
  {
    ...session,
    id: 'session-2',
    task: 'Second task',
    scores: { oneShot: 20, context: 17, control: 15, clarity: 21 },
    promptSmells: ['범위 기준이 늦게 정리됨']
  }
]);
assertIncludes(overall, '전체 흐름 리포트', 'overall report has title');
assertIncludes(overall, '가장 약한 축', 'overall report identifies weakest axis');
assertIncludes(overall, '축별 그래프', 'overall report includes text graph section');
assertIncludes(overall, '점수 비교표', 'overall report includes comparison table');
assertIncludes(overall, '대안 프롬프트', 'overall report includes alternative prompts');
assertIncludes(overall, '범위 기준이 늦게 정리됨 (2회)', 'overall report counts repeated smells');

const parsed = parseAiReportResult(`
AI 설명은 무시되어야 합니다.

\`\`\`json
{
  "summary": "선택 세션 평가",
  "scores": {
    "one_shot": 18,
    "context_drift": 17,
    "ai_control": 16,
    "prompt_clarity": 19,
    "total": 70
  },
  "prompt_smells": [
    {"type": "prompt_gap", "evidence": "범위가 늦게 정리됨", "fix": "완료 기준을 먼저 적기"}
  ],
  "good_examples": ["저장 시점을 직접 지정함"],
  "bad_examples": ["삭제 버튼 의미가 불명확함"],
  "next_actions": ["다음 요청에는 사용 흐름을 먼저 적기"]
}
\`\`\`
`);

assertEqual(parsed.summary, '선택 세션 평가', 'parser reads fenced JSON summary');
assertEqual(parsed.scores.oneShot, 18, 'parser maps CLI one_shot to extension oneShot');
assertEqual(parsed.scores.context, 17, 'parser maps CLI context_drift to extension context');
assertEqual(parsed.scores.control, 16, 'parser maps CLI ai_control to extension control');
assertEqual(parsed.scores.clarity, 19, 'parser maps CLI prompt_clarity to extension clarity');
assertIncludes(parsed.promptSmells[0], 'prompt_gap', 'parser converts object prompt smells');

console.log('ok - report flow parses AI JSON and creates free local scoring drafts');
