import { normalizeScores } from './scoring.js';
import type { VibeScores } from './types.js';
import type { VibeReportDraft } from './autoReport.js';

type JsonObject = Record<string, unknown>;

export function parseAiReportResult(raw: string): VibeReportDraft {
  const parsed = parseJsonObject(raw);
  const scores = parseScores(parsed.scores);

  return {
    summary: stringValue(parsed.summary) || 'AI가 생성한 리포트 요약입니다.',
    scores,
    promptSmells: stringList(parsed.promptSmells ?? parsed.prompt_smells),
    goodExamples: stringList(parsed.goodExamples ?? parsed.good_examples),
    badExamples: stringList(parsed.badExamples ?? parsed.bad_examples),
    nextActions: stringList(parsed.nextActions ?? parsed.next_actions)
  };
}

function parseJsonObject(raw: string): JsonObject {
  const candidate = extractJsonCandidate(raw.trim());
  if (!candidate) {
    throw new Error('JSON을 찾지 못했습니다.');
  }

  const value = JSON.parse(candidate) as unknown;
  if (!isObject(value)) {
    throw new Error('JSON 최상위 값은 객체여야 합니다.');
  }
  return value;
}

function extractJsonCandidate(raw: string): string | undefined {
  const fenced = raw.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenced?.[1]) {
    return fenced[1].trim();
  }

  const first = raw.indexOf('{');
  const last = raw.lastIndexOf('}');
  if (first >= 0 && last > first) {
    return raw.slice(first, last + 1);
  }

  return raw.startsWith('{') ? raw : undefined;
}

function parseScores(value: unknown): VibeScores {
  if (!isObject(value)) {
    throw new Error('scores 객체가 필요합니다.');
  }

  return normalizeScores({
    oneShot: numericValue(value.oneShot ?? value.one_shot),
    context: numericValue(value.context ?? value.context_drift),
    control: numericValue(value.control ?? value.ai_control),
    clarity: numericValue(value.clarity ?? value.prompt_clarity)
  });
}

function stringList(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => {
      if (typeof item === 'string') {
        return item.trim();
      }
      if (isObject(item)) {
        const type = stringValue(item.type);
        const evidence = stringValue(item.evidence);
        const fix = stringValue(item.fix);
        return [type, evidence, fix].filter(Boolean).join(' - ');
      }
      return '';
    })
    .filter(Boolean);
}

function stringValue(value: unknown): string {
  return typeof value === 'string' ? value.trim() : '';
}

function numericValue(value: unknown): number | undefined {
  const numeric = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(numeric) ? numeric : undefined;
}

function isObject(value: unknown): value is JsonObject {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
