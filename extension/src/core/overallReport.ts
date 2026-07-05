import { SCORE_KEYS, SCORE_LABELS, scoreTotal } from './scoring.js';
import type { VibeScores, VibeSession } from './types.js';

export function buildLocalOverallReport(sessions: VibeSession[]): string {
  if (sessions.length === 0) {
    return [
      '# VibeGraph 전체 흐름 리포트',
      '',
      '아직 기록된 세션이 없습니다. 먼저 현재 대화를 캡처해 주세요.'
    ].join('\n');
  }

  const scored = sessions.filter((session) => session.scores);
  const averages = axisAverages(scored);
  const weakest = weakestAxis(averages);
  const projectNames = uniqueNonEmpty(sessions.map((session) => session.project));
  const smells = repeatedSmells(sessions);

  return [
    '# VibeGraph 전체 흐름 리포트',
    '',
    '## 요약',
    '',
    `- 전체 세션: ${sessions.length}개`,
    `- 채점된 세션: ${scored.length}개`,
    `- 평균 점수: ${averageTotal(scored).toFixed(1)} / 100`,
    `- 가장 약한 축: ${weakest ? SCORE_LABELS[weakest] : '아직 판단 불가'}`,
    `- 프로젝트: ${projectNames.length > 0 ? projectNames.join(', ') : '미지정'}`,
    '',
    '## 4축 평균',
    '',
    ...SCORE_KEYS.map((key) => `- ${SCORE_LABELS[key]}: ${averages[key].toFixed(1)} / 25`),
    '',
    '## 축별 그래프',
    '',
    ...SCORE_KEYS.map((key) => `- ${SCORE_LABELS[key]} ${bar(averages[key])} ${averages[key].toFixed(1)}/25`),
    '',
    '## 점수 비교표',
    '',
    '| 항목 | 평균 | 해석 |',
    '| --- | ---: | --- |',
    ...SCORE_KEYS.map((key) => `| ${SCORE_LABELS[key]} | ${averages[key].toFixed(1)}/25 | ${scoreBand(averages[key])} |`),
    '',
    '## 반복 개선 신호',
    '',
    ...(smells.length > 0 ? smells.map((smell) => `- ${smell}`) : ['- 아직 반복 신호가 충분하지 않습니다.']),
    '',
    '## 다음 액션',
    '',
    ...nextActions(weakest).map((action) => `- ${action}`),
    '',
    '## 대안 프롬프트',
    '',
    ...alternativePrompts(weakest).map((prompt) => `- ${prompt}`),
    '',
    '## 최근 세션',
    '',
    ...sessions
      .slice(0, 5)
      .map((session) => `- ${session.task || session.title || '제목 없음'}: ${session.scores ? `${scoreTotal(session.scores)} / 100` : '미채점'}`)
  ].join('\n');
}

function axisAverages(sessions: VibeSession[]): VibeScores {
  if (sessions.length === 0) {
    return { oneShot: 0, context: 0, control: 0, clarity: 0 };
  }

  const totals = SCORE_KEYS.reduce(
    (acc, key) => ({ ...acc, [key]: 0 }),
    { oneShot: 0, context: 0, control: 0, clarity: 0 } as VibeScores
  );

  for (const session of sessions) {
    for (const key of SCORE_KEYS) {
      totals[key] += session.scores?.[key] ?? 0;
    }
  }

  return {
    oneShot: totals.oneShot / sessions.length,
    context: totals.context / sessions.length,
    control: totals.control / sessions.length,
    clarity: totals.clarity / sessions.length
  };
}

function weakestAxis(averages: VibeScores): keyof VibeScores | undefined {
  const scored = SCORE_KEYS.filter((key) => averages[key] > 0);
  if (scored.length === 0) {
    return undefined;
  }

  return scored.reduce((weakest, key) => (averages[key] < averages[weakest] ? key : weakest), scored[0]);
}

function averageTotal(sessions: VibeSession[]): number {
  if (sessions.length === 0) {
    return 0;
  }

  return sessions.reduce((total, session) => total + scoreTotal(session.scores), 0) / sessions.length;
}

function repeatedSmells(sessions: VibeSession[]): string[] {
  const counts = new Map<string, number>();
  for (const session of sessions) {
    for (const smell of session.promptSmells ?? []) {
      const key = smell.trim();
      if (key) {
        counts.set(key, (counts.get(key) ?? 0) + 1);
      }
    }
  }

  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([smell, count]) => `${smell} (${count}회)`);
}

function nextActions(weakest: keyof VibeScores | undefined): string[] {
  const defaults = [
    '작업 시작 프롬프트에 목표, 범위, 완료 기준을 한 번에 적습니다.',
    '작업 중간에 방향이 바뀌면 새 기준을 한 줄로 다시 고정합니다.',
    '작업 종료 전에 테스트/빌드/검증 결과를 확인하도록 요청합니다.'
  ];

  if (weakest === 'oneShot') {
    return ['첫 요청에 기대 산출물과 성공 조건을 더 구체적으로 적습니다.', ...defaults.slice(1)];
  }
  if (weakest === 'context') {
    return ['중간 전환점마다 현재 목표와 남은 작업을 짧게 재요약합니다.', ...defaults.slice(1)];
  }
  if (weakest === 'control') {
    return ['수정 금지 범위와 의사결정 기준을 먼저 선언합니다.', ...defaults.slice(1)];
  }
  if (weakest === 'clarity') {
    return ['파일 경로, 오류 메시지, 입력/출력 예시를 첫 요청에 포함합니다.', ...defaults.slice(1)];
  }
  return defaults;
}

function alternativePrompts(weakest: keyof VibeScores | undefined): string[] {
  if (weakest === 'oneShot') {
    return [
      '처음 요청에 "목표 / 수정 범위 / 완료 기준 / 검증 방법"을 네 줄로 나눠 적기',
      '원하는 산출물 예시를 하나 붙이고 "이 형식으로만 답해줘"라고 지정하기'
    ];
  }
  if (weakest === 'context') {
    return [
      '중간 전환 때 "현재 결정사항은 유지하고, 다음 변경만 적용해줘"라고 맥락을 잠그기',
      '긴 대화에서는 "지금까지의 기준을 5줄로 요약한 뒤 진행해줘"를 먼저 요청하기'
    ];
  }
  if (weakest === 'control') {
    return [
      '작업 전 "하지 말 것"과 "반드시 확인할 것"을 분리해서 적기',
      'AI가 제안만 하고 사용자가 선택할 항목은 "선택지는 제시하고 실행은 대기"라고 명시하기'
    ];
  }
  if (weakest === 'clarity') {
    return [
      '파일 경로, 오류 메시지, 기대 출력, 성공 조건을 한 프롬프트에 묶기',
      '모호한 표현 대신 숫자 기준이나 체크리스트로 완료 조건을 적기'
    ];
  }
  return [
    '목표, 입력, 제약, 완료 기준을 한 번에 적는 시작 템플릿을 쓰기',
    '작업 종료 전 테스트/빌드/검증 결과를 반드시 요약해 달라고 요청하기'
  ];
}

function bar(value: number): string {
  const filled = Math.max(0, Math.min(10, Math.round((value / 25) * 10)));
  return `${'█'.repeat(filled)}${'░'.repeat(10 - filled)}`;
}

function scoreBand(value: number): string {
  if (value >= 21) {
    return '강점';
  }
  if (value >= 16) {
    return '양호';
  }
  if (value >= 10) {
    return '보완 필요';
  }
  return '우선 개선';
}

function uniqueNonEmpty(values: string[]): string[] {
  return [...new Set(values.map((value) => value.trim()).filter(Boolean))];
}
