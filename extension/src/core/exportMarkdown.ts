import { SCORE_KEYS, SCORE_LABELS, scoreTotal } from './scoring.js';
import type { VibeSession } from './types.js';

function linesForMessages(session: VibeSession): string[] {
  if (session.messages.length === 0) {
    return ['No captured messages.'];
  }

  return session.messages.map((message) => {
    const role = message.role.toUpperCase();
    return `### ${message.order}. ${role}\n\n${message.text}`;
  });
}

function listOrEmpty(values: string[]): string {
  return values.length > 0 ? values.map((value) => `- ${value}`).join('\n') : '- 없음';
}

export function exportSessionMarkdown(session: VibeSession): string {
  const scoreLines = session.scores
    ? [
        `Total: ${scoreTotal(session.scores)} / 100`,
        '',
        ...SCORE_KEYS.map((key) => `- ${SCORE_LABELS[key]}: ${session.scores?.[key] ?? 0} / 25`)
      ]
    : ['아직 평가 전입니다.'];

  return [
    '# VibeGraph Session',
    '',
    '## Basic Info',
    '',
    `- Project: ${session.project || '미지정'}`,
    `- Task: ${session.task || '미지정'}`,
    `- Source: ${session.source}`,
    `- Title: ${session.title || '제목 없음'}`,
    `- URL: ${session.url || '없음'}`,
    `- Captured At: ${session.capturedAt}`,
    '',
    '## Scores',
    '',
    ...scoreLines,
    '',
    '## Report Summary',
    '',
    session.summary?.trim() || '아직 리포트 요약이 없습니다.',
    '',
    '## Tags',
    '',
    listOrEmpty(session.tags),
    '',
    '## Captured Conversation',
    '',
    ...linesForMessages(session),
    '',
    '## Notes',
    '',
    session.notes?.trim() || '없음',
    '',
    '## Prompt Smells',
    '',
    listOrEmpty(session.promptSmells ?? []),
    '',
    '## Good Examples',
    '',
    listOrEmpty(session.goodExamples ?? []),
    '',
    '## Bad Examples',
    '',
    listOrEmpty(session.badExamples ?? []),
    '',
    '## Next Actions',
    '',
    ...(session.nextActions?.length
      ? session.nextActions.map((action) => `- ${action}`)
      : [
          '- AI 대화창에 VibeGraph 리포트 프롬프트를 붙여 평가 JSON을 생성합니다.',
          '- 필요한 경우 JSON 백업을 보관한 뒤 기존 Python CLI 흐름과 비교합니다.'
        ]),
    ''
  ].join('\n');
}
