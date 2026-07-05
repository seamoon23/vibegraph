import { normalizeScores } from './scoring.js';
import type { VibeScores, VibeSession } from './types.js';

export type VibeReportDraft = {
  summary: string;
  scores: VibeScores;
  promptSmells: string[];
  goodExamples: string[];
  badExamples: string[];
  nextActions: string[];
};

export function buildLocalReportDraft(session: VibeSession): VibeReportDraft {
  const userMessages = session.messages.filter((message) => message.role === 'user');
  const messageText = session.messages.map((message) => message.text).join('\n');
  const userText = userMessages.length > 0 ? userMessages.map((message) => message.text).join('\n') : messageText;
  const sessionText = [
    session.title,
    session.project,
    session.task,
    session.notes,
    userText,
    ...(session.promptSmells ?? [])
  ]
    .filter(Boolean)
    .join('\n');
  const firstSignalText = userMessages[0]?.text ?? session.messages[0]?.text ?? session.task ?? session.title ?? session.notes ?? '';
  const turnCount = Math.max(userMessages.length || session.messages.length, session.messages.length);
  const repairSignals = countMatches(sessionText, /다시|아니|수정|오류|에러|안\s*돼|안됨|문제|틀렸|재시도|멈췄|실패|불친절|모호/g);
  const contextSignals = countMatches(sessionText, /앞서|아까|방금|이전|위에서|같은|반복|맥락|흐름|이어/g);
  const controlSignals = countMatches(sessionText, /반드시|하지\s*마|수정하지|기준|조건|경로|범위|먼저|확인|검증|저장|삭제|상위|루트/g);
  const claritySignals = countMatches(sessionText, /```|`[^`]+`|[A-Z]:\\|\/|\.ts|\.tsx|\.js|\.py|\.md|JSON|Markdown|npm|build|typecheck|테스트|빌드|검증|조건|목표|버튼|화면/g);
  const outcomeSignals = countMatches(sessionText, /완료|통과|성공|정리|리포트|저장|반영|생성|확인/g);
  const questionSignals = countMatches(sessionText, /\?|어떻게|왜|무엇|가능|될까|어찌/g);
  const wordDiversity = lexicalDiversity(sessionText);
  const specificityBonus = Math.min(6, claritySignals + Math.floor(wordDiversity / 18));
  const tieBreaker = scoreTieBreaker(sessionText);

  const scores = normalizeScores({
    oneShot:
      19 +
      Math.min(3, outcomeSignals) -
      Math.min(8, Math.max(0, turnCount - 5)) -
      Math.min(10, repairSignals * 2) +
      tieBreaker.oneShot,
    context:
      16 +
      Math.min(5, contextSignals) +
      Math.min(3, outcomeSignals) -
      Math.min(7, Math.max(0, turnCount - 10)) -
      Math.min(5, repairSignals) +
      tieBreaker.context,
    control:
      10 +
      Math.min(10, controlSignals * 2) +
      Math.min(3, outcomeSignals) -
      Math.min(4, questionSignals) -
      Math.min(4, repairSignals) +
      tieBreaker.control,
    clarity:
      9 +
      specificityBonus +
      Math.min(5, Math.floor(firstSignalText.length / 90)) -
      Math.min(3, questionSignals) +
      tieBreaker.clarity
  });

  return {
    summary: buildSummary(session, scores),
    scores,
    promptSmells: buildPromptSmells(scores, repairSignals, contextSignals),
    goodExamples: buildGoodExamples(firstSignalText, controlSignals, claritySignals),
    badExamples: buildBadExamples(repairSignals, contextSignals),
    nextActions: buildNextActions(scores)
  };
}

function buildSummary(session: VibeSession, scores: VibeScores): string {
  const task = session.task || session.title || '제목 없는 작업';
  const total = scores.oneShot + scores.context + scores.control + scores.clarity;
  return `${session.source} 대화 "${task}"를 메시지 ${session.messages.length}개 기준으로 무료 초안 채점했습니다. 총점은 ${total}/100이며, 실제 판단 전 참고용으로 사용하세요.`;
}

function buildPromptSmells(scores: VibeScores, repairSignals: number, contextSignals: number): string[] {
  const smells: string[] = [];
  if (scores.oneShot < 15 || repairSignals > 1) {
    smells.push('초기 요청에서 완료 조건이나 기대 산출물이 덜 분명해 후속 수정이 늘어났습니다.');
  }
  if (scores.context < 15 || contextSignals > 1) {
    smells.push('중간 맥락을 다시 설명하는 신호가 있어 컨텍스트 유지가 약했습니다.');
  }
  if (scores.control < 15) {
    smells.push('작업 범위와 판단 기준을 사용자가 더 강하게 잡아줄 필요가 있습니다.');
  }
  if (scores.clarity < 15) {
    smells.push('요청에 파일 경로, 에러, 검증 기준 같은 구체 정보가 부족했습니다.');
  }
  return smells.length > 0 ? smells : ['뚜렷한 프롬프트 냄새는 적지만, 점수는 보수적으로 확인하세요.'];
}

function buildGoodExamples(firstUserText: string, controlSignals: number, claritySignals: number): string[] {
  const examples: string[] = [];
  if (controlSignals > 0) {
    examples.push('수정 금지 범위, 검증 기준, 작업 순서처럼 사용자가 주도권을 잡는 표현이 포함됐습니다.');
  }
  if (claritySignals > 0) {
    examples.push('파일명, 경로, 테스트, 오류처럼 AI가 바로 행동할 수 있는 단서가 제공됐습니다.');
  }
  if (firstUserText.trim()) {
    examples.push(`초기 요청 예시: ${excerpt(firstUserText)}`);
  }
  return examples.slice(0, 3);
}

function buildBadExamples(repairSignals: number, contextSignals: number): string[] {
  const examples: string[] = [];
  if (repairSignals > 0) {
    examples.push('수정/오류/재시도 신호가 있어 첫 요청만으로 충분히 닫히지 않은 부분이 있었습니다.');
  }
  if (contextSignals > 0) {
    examples.push('앞선 맥락을 다시 짚는 표현이 있어 작업 흐름이 중간에 흔들렸을 수 있습니다.');
  }
  return examples.length > 0 ? examples : ['무료 초안 기준으로 큰 아쉬운 예시는 감지되지 않았습니다.'];
}

function buildNextActions(scores: VibeScores): string[] {
  const actions = [
    '다음 작업에서는 첫 요청에 목표, 수정 금지 범위, 완료 기준을 한 번에 적어보세요.',
    '작업 중간에 방향이 바뀌면 새 기준을 한 줄로 다시 고정하세요.',
    '중요한 결과물은 마지막에 테스트/빌드/확인 명령까지 요청하세요.'
  ];

  if (scores.clarity < 15) {
    actions.unshift('다음 프롬프트에는 파일 경로, 입력 예시, 기대 출력 형식을 더 구체적으로 넣으세요.');
  }

  return actions.slice(0, 3);
}

function countMatches(value: string, pattern: RegExp): number {
  return value.match(pattern)?.length ?? 0;
}

function lexicalDiversity(value: string): number {
  const words = value
    .toLowerCase()
    .split(/[^a-z0-9가-힣_./\\-]+/g)
    .map((word) => word.trim())
    .filter((word) => word.length > 1);
  return new Set(words).size;
}

function scoreTieBreaker(value: string): VibeScores {
  const hash = [...value].reduce((acc, char) => (acc * 31 + char.charCodeAt(0)) >>> 0, 2166136261);
  return {
    oneShot: (hash % 5) - 2,
    context: (Math.floor(hash / 7) % 5) - 2,
    control: (Math.floor(hash / 17) % 5) - 2,
    clarity: (Math.floor(hash / 29) % 5) - 2
  };
}

function excerpt(value: string): string {
  const normalized = value.replace(/\s+/g, ' ').trim();
  return normalized.length > 90 ? `${normalized.slice(0, 90)}...` : normalized;
}
