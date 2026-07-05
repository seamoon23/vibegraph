import { SCORE_KEYS, SCORE_LABELS, isCompleteScoreSet, scoreTotal } from '../../core/scoring.js';
import type { VibeScores } from '../../core/types.js';
import { escapeHtml } from './html.js';

type Preset = {
  label: string;
  value: number;
  hint: string;
};

const PRESETS: Preset[] = [
  { label: '부족', value: 0, hint: '거의 안 됨' },
  { label: '낮음', value: 6, hint: '자주 막힘' },
  { label: '보통', value: 12, hint: '절반 정도' },
  { label: '좋음', value: 18, hint: '대체로 좋음' },
  { label: '매우 좋음', value: 25, hint: '거의 완성' }
];

export function ScoreEditorContent(scores: VibeScores | undefined): string {
  const fields = SCORE_KEYS.map((key) => {
    const value = scores?.[key];
    const buttons = PRESETS.map((preset) => {
      const active = value === preset.value ? ' active' : '';
      return `
        <button
          class="score-preset${active}"
          data-score-preset="${key}:${preset.value}"
          title="${escapeHtml(preset.hint)}"
          aria-pressed="${active ? 'true' : 'false'}"
        >
          <strong>${preset.value}</strong>
          <span>${escapeHtml(preset.label)}</span>
        </button>
      `;
    }).join('');

    return `
      <div class="score-card">
        <div class="score-card-head">
          <div>
            <h3>${escapeHtml(SCORE_LABELS[key])}</h3>
            <p>${escapeHtml(scoreHelp(key))}</p>
          </div>
          <div class="score-current">${value ?? '-'}<span>/25</span></div>
        </div>
        <div class="score-rubric">${escapeHtml(scoreRubric(key))}</div>
        <div class="score-presets">${buttons}</div>
        <details class="manual-score">
          <summary>직접 숫자 입력</summary>
          <label>
            0~25점 사이로 미세 조정
            <input data-score="${key}" type="number" min="0" max="25" step="1" value="${escapeHtml(value ?? '')}" />
          </label>
        </details>
      </div>
    `;
  }).join('');

  const total = isCompleteScoreSet(scores)
    ? `<div class="score-total">총점: ${scoreTotal(scores)} / 100</div>`
    : '<p class="muted">아직 평가 전입니다. 각 축에서 가장 가까운 버튼을 하나씩 누르면 총점이 계산됩니다.</p>';

  return `
    <div class="score-editor-content" id="score-editor">
      <div class="score-helper">
        직접 판단할 때만 4축 점수를 입력하세요. 이 입력도 저장 전까지는 임시 변경입니다.
      </div>
      <div class="score-grid">${fields}</div>
      ${total}
    </div>
  `;
}

export function ScoreEditor(scores: VibeScores | undefined): string {
  return `
    <section class="panel" id="score-editor-panel">
      <div class="score-title-row">
        <div>
          <h2>4축 점수</h2>
          <p class="muted">각 축은 0~25점입니다. 먼저 버튼으로 빠르게 고르고, 필요할 때만 숫자로 미세 조정하세요.</p>
        </div>
        <button class="ghost small" data-action="open-guide">사용 가이드</button>
      </div>
      ${ScoreEditorContent(scores)}
    </section>
  `;
}

function scoreHelp(key: keyof VibeScores): string {
  const help: Record<keyof VibeScores, string> = {
    oneShot: '처음 요청만으로 원하는 방향까지 얼마나 갔나요?',
    context: '중간에 같은 설명을 반복하지 않아도 맥락이 유지됐나요?',
    control: 'AI가 산으로 가지 않고 내가 방향을 잡고 있었나요?',
    clarity: '요청이 구체적이고 바로 실행 가능한 형태였나요?'
  };
  return help[key];
}

function scoreRubric(key: keyof VibeScores): string {
  const rubrics: Record<keyof VibeScores, string> = {
    oneShot: '낮음: 계속 재요청함 · 보통: 절반쯤 맞음 · 높음: 첫 요청부터 거의 맞음',
    context: '낮음: 맥락을 자주 잃음 · 보통: 가끔 보정함 · 높음: 흐름을 잘 이어감',
    control: '낮음: AI가 방향을 끌고 감 · 보통: 함께 조정함 · 높음: 내가 기준을 명확히 잡음',
    clarity: '낮음: 모호함 · 보통: 핵심은 있음 · 높음: 범위/조건/출력이 분명함'
  };
  return rubrics[key];
}
