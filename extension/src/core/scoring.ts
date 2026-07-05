import type { VibeScores } from './types.js';

export const SCORE_KEYS: Array<keyof VibeScores> = [
  'oneShot',
  'context',
  'control',
  'clarity'
];

export const SCORE_LABELS: Record<keyof VibeScores, string> = {
  oneShot: '원샷 성공률',
  context: '컨텍스트 유지력',
  control: '주도권 제어력',
  clarity: '프롬프트 선명도'
};

export function clampScore(value: unknown): number {
  const numeric = typeof value === 'number' ? value : Number(value);
  if (!Number.isFinite(numeric)) {
    return 0;
  }

  return Math.min(25, Math.max(0, Math.round(numeric)));
}

export function normalizeScores(scores: Partial<VibeScores>): VibeScores {
  return {
    oneShot: clampScore(scores.oneShot),
    context: clampScore(scores.context),
    control: clampScore(scores.control),
    clarity: clampScore(scores.clarity)
  };
}

export function scoreTotal(scores?: Partial<VibeScores>): number {
  if (!scores) {
    return 0;
  }

  return SCORE_KEYS.reduce((total, key) => total + clampScore(scores[key]), 0);
}

export function isCompleteScoreSet(scores?: Partial<VibeScores>): scores is VibeScores {
  if (!scores) {
    return false;
  }

  return SCORE_KEYS.every((key) => Number.isFinite(Number(scores[key])));
}
