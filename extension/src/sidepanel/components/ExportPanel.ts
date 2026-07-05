import { SCORE_KEYS, SCORE_LABELS, scoreTotal } from '../../core/scoring.js';
import type { VibeScores, VibeSession } from '../../core/types.js';
import { escapeHtml } from './html.js';
import { ScoreEditorContent } from './ScoreEditor.js';

export type SelectedEvalMode = 'manual' | 'local' | 'ai';
export type OverallReportMode = 'local' | 'ai';

type ExportPanelOptions = {
  view: 'session' | 'overall';
  session: VibeSession | undefined;
  sessionCount: number;
  selectedEvalMode: SelectedEvalMode;
  overallReportMode: OverallReportMode;
  overallReportMarkdown?: string;
  overallReportUpdatedAt?: string;
  githubUrl: string;
};

export function ExportPanel(options: ExportPanelOptions): string {
  const disabled = options.session ? '' : ' disabled';
  const hasSessions = options.sessionCount > 0;

  if (options.view === 'overall') {
    return `
      <section class="panel">
        <h2>전체 리포트</h2>
        ${overallReportWorkflow(options)}
        ${exportAndHelp(options, disabled, hasSessions)}
      </section>
    `;
  }

  return `
    <section class="panel">
      <h2>개별 리포트</h2>
      ${options.session ? selectedReportPreview(options.session) : '<p class="muted">대화 관리 탭에서 세션을 선택하면 개별 리포트가 표시됩니다.</p>'}
      ${selectedEvalWorkflow(options.selectedEvalMode, disabled, options.session)}
      ${exportAndHelp(options, disabled, hasSessions)}
    </section>
  `;
}

function selectedEvalWorkflow(mode: SelectedEvalMode, disabled: string, session: VibeSession | undefined): string {
  return `
    <div class="workflow-section" id="evaluation-panel">
      <h3>선택 세션 평가</h3>
      <div class="segmented" role="tablist" aria-label="선택 세션 평가 방식">
        <button class="${mode === 'manual' ? 'active' : ''}" data-action="set-selected-eval-mode" data-eval-mode="manual">직접 입력</button>
        <button class="${mode === 'local' ? 'active' : ''}" data-action="set-selected-eval-mode" data-eval-mode="local">무료 초안</button>
        <button class="${mode === 'ai' ? 'active' : ''}" data-action="set-selected-eval-mode" data-eval-mode="ai">AI 평가</button>
      </div>
      ${
        mode === 'manual'
          ? `
            <div class="method-panel manual-eval-panel">
              <p>직접 판단하고 싶은 경우만 열어 쓰세요. 각 축은 0~25점이며, 저장 전까지는 임시 변경입니다.</p>
              ${session ? ScoreEditorContent(session.scores) : '<p class="muted">세션을 선택하면 4축 입력이 표시됩니다.</p>'}
            </div>
          `
          : mode === 'local'
          ? `
            <div class="method-panel">
              <p>더미데이터가 아니라 브라우저 안에서 대화 텍스트를 규칙으로 훑어 만든 참고용 추정입니다. 외부 호출은 없습니다.</p>
              <ul class="method-notes">
                <li>수정, 오류, 재시도 표현이 많으면 원샷 성공률을 낮게 봅니다.</li>
                <li>파일 경로, 조건, 검증, 출력 형식이 보이면 프롬프트 선명도를 높게 봅니다.</li>
                <li>범위, 금지사항, 저장/삭제 기준처럼 사용자가 주도한 단서가 있으면 제어력을 높게 봅니다.</li>
                <li>AI 의미판단이 아니므로 최종 평가는 직접 입력이나 AI 평가로 보정하는 용도입니다.</li>
              </ul>
              <button class="secondary" data-action="score-selected-local"${disabled}>선택 세션 무료 초안 생성</button>
            </div>
          `
          : `
            <div class="method-panel">
              <p>AI 대화창에 평가 프롬프트를 붙여넣고, AI가 돌려준 JSON을 아래 칸에 넣으면 선택 세션의 점수/요약/다음 액션을 갱신합니다.</p>
              <div class="actions compact-actions">
                <button class="secondary" data-action="copy-prompt"${disabled}>AI 평가 프롬프트 복사</button>
              </div>
              <label class="ai-result-box">
                AI 응답 JSON 붙여넣기
                <textarea
                  data-ai-result
                  placeholder='{"summary":"...","scores":{"oneShot":18,"context":17,"control":16,"clarity":19},"promptSmells":[],"goodExamples":[],"badExamples":[],"nextActions":[]}'
                  ${disabled}
                ></textarea>
              </label>
              <button class="primary" data-action="apply-ai-result"${disabled}>붙여넣은 JSON으로 선택 리포트 갱신</button>
              <p class="muted">갱신 후 위쪽 세션 정보의 수정정보 저장을 눌러야 로컬 기록에 확정됩니다.</p>
            </div>
          `
      }
    </div>
  `;
}

function overallReportWorkflow(options: ExportPanelOptions): string {
  const hasSessions = options.sessionCount > 0;
  const disabled = hasSessions ? '' : ' disabled';
  const report = options.overallReportMarkdown
    ? renderMarkdownPreview(options.overallReportMarkdown)
    : '<p class="muted">아직 전체 흐름 리포트가 없습니다. 무료 요약을 생성하거나 AI 전체 리포트를 붙여넣어 보세요.</p>';

  return `
    <div class="workflow-section overall-section">
      <div class="report-preview-head">
        <h3>전체 흐름 리포트</h3>
        ${options.overallReportUpdatedAt ? `<strong>${escapeHtml(options.overallReportUpdatedAt)}</strong>` : ''}
      </div>
      <div class="overall-preview">${report}</div>
      <div class="segmented" role="tablist" aria-label="전체 흐름 리포트 방식">
        <button class="${options.overallReportMode === 'local' ? 'active' : ''}" data-action="set-overall-report-mode" data-overall-mode="local">무료 요약</button>
        <button class="${options.overallReportMode === 'ai' ? 'active' : ''}" data-action="set-overall-report-mode" data-overall-mode="ai">AI 전체 리포트</button>
      </div>
      ${
        options.overallReportMode === 'local'
          ? `
            <div class="method-panel">
              <p>전체 세션의 평균 점수, 가장 약한 축, 반복 개선 신호를 확장기능 안에서 바로 요약합니다.</p>
              <div class="actions compact-actions">
                <button class="secondary" data-action="generate-overall-local"${disabled}>전체 흐름 요약 생성</button>
                <button class="ghost" data-action="score-all-local"${disabled}>모든 세션 개별 초안 채우기</button>
              </div>
            </div>
          `
          : `
            <div class="method-panel">
              <p>여러 세션을 한 번에 보고 패턴, 약한 축, 반복되는 Prompt Smell을 AI에게 평가받습니다. 결과는 Markdown 그대로 붙여넣으면 됩니다.</p>
              <button class="secondary" data-action="copy-all-prompt"${disabled}>전체 리포트 프롬프트 복사</button>
              <label class="ai-result-box">
                AI 전체 리포트 Markdown 붙여넣기
                <textarea data-overall-ai-report placeholder="# 전체 흐름 리포트&#10;&#10;- 전체 패턴..."></textarea>
              </label>
              <button class="primary" data-action="apply-overall-report"${disabled}>붙여넣은 Markdown을 전체 흐름 리포트로 보기</button>
            </div>
          `
      }
    </div>
  `;
}

function exportAndHelp(options: ExportPanelOptions, disabled: string, hasSessions: boolean): string {
  return `
    <details class="utility-panel">
      <summary>내보내기 / 추가설정</summary>
      <div class="actions">
        <button class="ghost" data-action="export-md"${disabled}>선택 Markdown 저장</button>
        <button class="ghost" data-action="export-json"${disabled}>선택 JSON 백업</button>
        <button class="ghost" data-action="backup-json"${hasSessions ? '' : ' disabled'}>전체 백업 JSON</button>
        <button class="ghost" data-action="export-overall-md"${options.overallReportMarkdown ? '' : ' disabled'}>전체 리포트 Markdown 저장</button>
      </div>
      <div class="cli-guide">
        <h3>CLI와 함께 쓰려면</h3>
        <p>확장기능은 브라우저 대화를 빠르게 캡처하고 평가하는 Lite 도구입니다. 기존 Python CLI는 로컬 파일 기반 리포트, 대시보드, 성장 리포트 흐름을 계속 담당합니다.</p>
        <p>접근 경로: PowerShell 또는 Windows Terminal &gt; <code>cd C:\\codex\\app\\vibegraph</code> &gt; <code>vibe report</code> 또는 <code>vibe growth</code></p>
        <p><a href="${escapeHtml(options.githubUrl)}" target="_blank" rel="noreferrer">GitHub에서 VibeGraph 안내 보기</a></p>
      </div>
    </details>
  `;
}

function selectedReportPreview(session: VibeSession): string {
  const total = session.scores ? scoreTotal(session.scores) : 0;
  const grade = gradeForTotal(total);
  const scoreLine = session.scores ? `총점 ${total} / 100` : '아직 점수 없음';
  const focus = session.scores ? weakestAxis(session.scores) : undefined;
  const nextActions = session.nextActions?.length
    ? actionList(session.nextActions)
    : '<p class="report-empty">무료 초안 또는 AI 평가 후 다음 액션이 표시됩니다.</p>';
  const smells = session.promptSmells?.length
    ? smellCards(session.promptSmells)
    : '<p class="report-empty">아직 개선 신호가 없습니다.</p>';
  const examples = examplesGrid(session.goodExamples ?? [], session.badExamples ?? []);

  return `
    <div class="report-board">
      <section class="report-hero ${grade.tone}">
        <div class="grade-badge">${escapeHtml(grade.label)}</div>
        <div class="hero-copy">
          <h3>선택 리포트</h3>
          <p>${escapeHtml(session.summary || '아직 리포트 요약이 없습니다.')}</p>
          <div class="report-chips">
            <span>${escapeHtml(session.source)}</span>
            <span>메시지 ${session.messages.length}개</span>
            <span>${escapeHtml(session.capturedAt.slice(0, 10))}</span>
          </div>
        </div>
        <div class="total-score"><strong>${session.scores ? total : '-'}</strong><span>/100</span></div>
      </section>

      ${session.scores ? `
        <div class="report-grid-2">
          <section class="report-card">
            <div class="card-title-row">
              <h4>세부 점수</h4>
              <span>${escapeHtml(scoreLine)}</span>
            </div>
            ${scoreBars(session.scores)}
          </section>
          <section class="report-card radar-card">
            <h4>레이더 차트</h4>
            ${radarChart(session.scores)}
          </section>
        </div>
        <section class="report-card focus-card">
          <h4>지금 집중할 항목</h4>
          <p><b>${focus ? escapeHtml(SCORE_LABELS[focus]) : '아직 판단 불가'}</b>${focus ? ` - ${escapeHtml(focusAdvice(focus))}` : ''}</p>
        </section>
      ` : ''}

      <section class="report-card smell-section">
        <h4>Prompt Smell 감지</h4>
        ${smells}
      </section>

      <section class="report-card">
        <h4>프롬프트 리팩토링 가이드</h4>
        ${examples}
      </section>

      <section class="report-card action-section">
        <h4>다음 액션</h4>
        ${nextActions}
      </section>
    </div>
  `;
}

function scoreBars(scores: VibeScores): string {
  const rows = SCORE_KEYS.map((key) => {
    const value = scores[key];
    const percent = Math.round((value / 25) * 100);
    return `
      <div class="axis-score-row">
        <span>${escapeHtml(SCORE_LABELS[key])}</span>
        <div><i style="width:${percent}%"></i></div>
        <b>${value}/25</b>
      </div>
    `;
  }).join('');

  return `<div class="axis-score-grid">${rows}</div>`;
}

function renderMarkdownPreview(markdown: string): string {
  const lines = markdown
    .trim()
    .split(/\r?\n/)
    .map((line) => line.trimEnd());
  const title = findMarkdownTitle(lines);
  const sections: Array<{ title: string; lines: string[] }> = [];
  let current: { title: string; lines: string[] } | undefined;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || isMarkdownDivider(trimmed) || trimmed.startsWith('```')) {
      continue;
    }

    const heading = markdownHeadingTitle(trimmed);
    if (heading) {
      if (normalizeTitle(heading) === normalizeTitle(title)) {
        continue;
      }
      current = { title: heading, lines: [] };
      sections.push(current);
      continue;
    }

    const numbered = numberedSectionTitle(trimmed);
    if (numbered) {
      current = { title: numbered, lines: [] };
      sections.push(current);
      continue;
    }

    if (!current && trimmed !== title) {
      current = { title: '종합 패턴', lines: [] };
      sections.push(current);
    }

    if (current) {
      current.lines.push(trimmed);
    }
  }

  const cards = sections.length > 0
    ? sections.map((section) => renderMarkdownSection(section)).join('')
    : `<section class="overall-card">${renderMarkdownLines(lines)}</section>`;
  const hero = renderOverallHero(title, lines);

  return `
    <div class="overall-report-board">
      ${hero}
      <div class="overall-card-grid">${cards}</div>
    </div>
  `;
}

function renderOverallHero(title: string, lines: string[]): string {
  const cleaned = lines.map((line) => cleanMarkdownInline(line.trim())).filter(Boolean);
  const totalSessions = findMetricValue(cleaned, '전체 세션');
  const scoredSessions = findMetricValue(cleaned, '채점된 세션');
  const averageScore = findMetricValue(cleaned, '평균 점수');
  const weakestAxis = findMetricValue(cleaned, '가장 약한 축') ?? findWeakestAxisFromLines(cleaned);
  const scoreNumber = averageScore?.match(/([0-9]+(?:\.[0-9]+)?)\s*\/\s*100/)?.[1];
  const scorePercent = scoreNumber ? Math.max(0, Math.min(100, Number(scoreNumber))) : 0;
  const focus = weakestAxis ? `가장 먼저 볼 축은 ${weakestAxis}입니다.` : '세션 흐름과 반복 신호를 먼저 훑어보세요.';

  return `
    <section class="overall-hero">
      <div class="overall-hero-main">
        <span>FLOW REPORT</span>
        <h4>${escapeHtml(title)}</h4>
        <p>${escapeHtml(focus)}</p>
      </div>
      <div class="overall-hero-score">
        <strong>${scoreNumber ? escapeHtml(scoreNumber) : '-'}</strong>
        <span>/100</span>
      </div>
      <div class="overall-hero-bar" aria-hidden="true">
        <i style="width:${scorePercent}%"></i>
      </div>
      <div class="overall-hero-metrics">
        ${heroMetric('전체 세션', totalSessions)}
        ${heroMetric('채점됨', scoredSessions)}
        ${heroMetric('약한 축', weakestAxis)}
      </div>
    </section>
  `;
}

function heroMetric(label: string, value: string | undefined): string {
  if (!value) {
    return '';
  }

  return `
    <div>
      <span>${escapeHtml(label)}</span>
      <b>${escapeHtml(value)}</b>
    </div>
  `;
}

function renderMarkdownSection(section: { title: string; lines: string[] }): string {
  const special = renderSpecialOverallSection(section);
  if (special) {
    return special;
  }

  return `
    <section class="overall-card ${sectionClass(section.title)}">
      <h5>${escapeHtml(sectionIcon(section.title))} ${escapeHtml(section.title)}</h5>
      ${renderNarrativeCards(section.lines)}
    </section>
  `;
}

function renderSpecialOverallSection(section: { title: string; lines: string[] }): string | undefined {
  if (section.title.includes('요약')) {
    return renderOverallSummary(section);
  }
  if (section.title.includes('종합') || section.title.includes('패턴') || section.title.toLowerCase().includes('overall')) {
    return renderOverallNarrative(section);
  }
  if (section.title.includes('4축 평균') || section.title.includes('축별 그래프')) {
    return renderOverallAxis(section);
  }
  if (section.title.includes('점수 비교표')) {
    return renderOverallComparison(section);
  }
  if (section.title.includes('반복 개선 신호') || section.title.includes('Prompt Smell') || section.title.includes('스멜')) {
    return renderOverallSignalCards(section);
  }
  if (section.title.includes('다음 액션') || section.title.includes('대안 프롬프트') || section.title.includes('권장') || section.title.includes('추천') || section.title.includes('개선')) {
    return renderOverallActionCards(section);
  }
  if (section.title.includes('최근 세션')) {
    return renderRecentSessionCards(section);
  }
  return undefined;
}

function renderOverallNarrative(section: { title: string; lines: string[] }): string | undefined {
  const content = renderNarrativeCards(section.lines);
  if (!content) {
    return undefined;
  }

  return `
    <section class="overall-card summary-card-v2">
      <h5>핵심 ${escapeHtml(section.title)}</h5>
      ${content}
    </section>
  `;
}

function renderOverallSummary(section: { title: string; lines: string[] }): string {
  const items = section.lines
    .filter((line) => line.startsWith('- '))
    .map((line) => parseLabelValue(line.slice(2)));

  return `
    <section class="overall-card summary-card-v2">
      <h5>핵심 ${escapeHtml(section.title)}</h5>
      <div class="overall-kpi-grid">
        ${items.map((item) => `
          <div class="overall-kpi">
            <span>${escapeHtml(item.label)}</span>
            <strong>${escapeHtml(item.value)}</strong>
          </div>
        `).join('')}
      </div>
    </section>
  `;
}

function renderOverallAxis(section: { title: string; lines: string[] }): string | undefined {
  const axisRows = section.lines
    .filter((line) => line.startsWith('- '))
    .map((line) => parseAxisLine(line.slice(2)))
    .filter((item): item is { label: string; value: number; display: string } => Boolean(item));

  if (axisRows.length === 0) {
    return undefined;
  }

  return `
    <section class="overall-card analysis">
      <h5>분석 ${escapeHtml(section.title)}</h5>
      <div class="overall-axis-grid">
        ${axisRows.map((axis) => {
          const percent = Math.max(0, Math.min(100, Math.round((axis.value / 25) * 100)));
          return `
            <div class="overall-axis-row">
              <span>${escapeHtml(axis.label)}</span>
              <div><i style="width:${percent}%"></i></div>
              <b>${escapeHtml(axis.display)}</b>
            </div>
          `;
        }).join('')}
      </div>
    </section>
  `;
}

function renderOverallComparison(section: { title: string; lines: string[] }): string | undefined {
  const rows = section.lines
    .filter((line) => line.startsWith('|') && !line.includes('---') && !line.includes('항목'))
    .map(parseTableRow)
    .filter((row): row is string[] => row.length >= 3);

  if (rows.length === 0) {
    return undefined;
  }

  return `
    <section class="overall-card analysis">
      <h5>분석 ${escapeHtml(section.title)}</h5>
      <div class="overall-compare-list">
        ${rows.map(([label, score, note]) => `
          <div class="overall-compare-row">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(score)}</strong>
            <em>${escapeHtml(note)}</em>
          </div>
        `).join('')}
      </div>
    </section>
  `;
}

function renderOverallSignalCards(section: { title: string; lines: string[] }): string | undefined {
  const items = bulletValues(section.lines);
  if (items.length === 0) {
    const content = renderNarrativeCards(section.lines);
    return content
      ? `
        <section class="overall-card warn">
          <h5>감지 ${escapeHtml(section.title)}</h5>
          ${content}
        </section>
      `
      : undefined;
  }

  return `
    <section class="overall-card warn">
      <h5>감지 ${escapeHtml(section.title)}</h5>
      <div class="overall-signal-list">
        ${items.map((item, index) => `
          <div class="overall-signal-item">
            <span>${index + 1}</span>
            <p>${escapeHtml(item)}</p>
          </div>
        `).join('')}
      </div>
    </section>
  `;
}

function renderOverallActionCards(section: { title: string; lines: string[] }): string | undefined {
  const items = bulletValues(section.lines);
  if (items.length === 0) {
    const content = renderNarrativeCards(section.lines);
    return content
      ? `
        <section class="overall-card accent">
          <h5>개선 ${escapeHtml(section.title)}</h5>
          ${content}
        </section>
      `
      : undefined;
  }

  return `
    <section class="overall-card accent">
      <h5>개선 ${escapeHtml(section.title)}</h5>
      <div class="overall-action-list">
        ${items.map((item) => `
          <div class="overall-action-item">${escapeHtml(item)}</div>
        `).join('')}
      </div>
    </section>
  `;
}

function renderRecentSessionCards(section: { title: string; lines: string[] }): string | undefined {
  const items = bulletValues(section.lines);
  if (items.length === 0) {
    return undefined;
  }

  return `
    <section class="overall-card">
      <h5>기록 ${escapeHtml(section.title)}</h5>
      <div class="overall-session-list">
        ${items.map((item) => {
          const parsed = parseLabelValue(item);
          return `
            <div class="overall-session-item">
              <span>${escapeHtml(parsed.label)}</span>
              <strong>${escapeHtml(parsed.value)}</strong>
            </div>
          `;
        }).join('')}
      </div>
    </section>
  `;
}

function renderMarkdownLines(lines: string[]): string {
  return lines
    .map((line) => {
      if (line.startsWith('- ')) {
        const value = cleanMarkdownInline(line.slice(2));
        const chart = value.includes('█') || value.includes('░') ? ' text-chart-line' : '';
        return `<p class="markdown-bullet${chart}">• ${escapeHtml(value)}</p>`;
      }
      if (line.startsWith('|')) {
        return `<p class="markdown-table-line">${escapeHtml(line)}</p>`;
      }
      return `<p>${escapeHtml(cleanMarkdownInline(line))}</p>`;
    })
    .join('');
}

function renderNarrativeCards(lines: string[]): string {
  const items = lines
    .filter((line) => line.trim() && !isMarkdownDivider(line.trim()) && !line.startsWith('|'))
    .map((line) => cleanMarkdownInline(line.replace(/^-+\s*/, '').trim()))
    .filter(Boolean);

  if (items.length === 0) {
    return '';
  }

  return `
    <div class="overall-narrative-list">
      ${items.map((item) => {
        const lead = splitLead(item);
        return `
          <div class="overall-narrative-item">
            ${lead ? `<b>${escapeHtml(lead.label)}</b><p>${escapeHtml(lead.body)}</p>` : `<p>${escapeHtml(item)}</p>`}
          </div>
        `;
      }).join('')}
    </div>
  `;
}

function bulletValues(lines: string[]): string[] {
  return lines
    .filter((line) => /^[-*]\s+/.test(line.trim()))
    .map((line) => cleanMarkdownInline(line.trim().replace(/^[-*]\s+/, '')))
    .filter(Boolean);
}

function findMetricValue(lines: string[], label: string): string | undefined {
  for (const line of lines) {
    const normalized = line.replace(/^[-*]\s+/, '').trim();
    const parsed = parseLabelValue(normalized);
    if (normalizeTitle(parsed.label) === normalizeTitle(label)) {
      return parsed.value || undefined;
    }
  }
  return undefined;
}

function findWeakestAxisFromLines(lines: string[]): string | undefined {
  const axes = lines
    .map((line) => parseAxisLine(line.replace(/^[-*]\s+/, '').trim()))
    .filter((axis): axis is { label: string; value: number; display: string } => Boolean(axis));

  if (axes.length === 0) {
    return undefined;
  }

  const weakest = axes.reduce((current, axis) => (axis.value < current.value ? axis : current), axes[0]);
  return `${weakest.label} ${weakest.display}`;
}

function parseLabelValue(value: string): { label: string; value: string } {
  const [label, ...rest] = value.split(':');
  if (rest.length === 0) {
    return { label: value, value: '' };
  }
  return {
    label: label.trim(),
    value: rest.join(':').trim()
  };
}

function parseAxisLine(value: string): { label: string; value: number; display: string } | undefined {
  const withoutChart = cleanMarkdownInline(value).replace(/[█░]+/g, '').trim();
  const match = withoutChart.match(/^(.+?)[:\s]+([0-9]+(?:\.[0-9]+)?)\s*\/\s*25/);
  if (!match) {
    return undefined;
  }
  const numeric = Number(match[2]);
  if (!Number.isFinite(numeric)) {
    return undefined;
  }
  return {
    label: match[1].trim(),
    value: numeric,
    display: `${numeric.toFixed(Number.isInteger(numeric) ? 0 : 1)}/25`
  };
}

function parseTableRow(line: string): string[] {
  return line
    .split('|')
    .map((cell) => cell.trim())
    .filter(Boolean);
}

function findMarkdownTitle(lines: string[]): string {
  const heading = lines.map((line) => markdownHeadingTitle(line.trim())).find(Boolean);
  if (heading) {
    return heading;
  }

  const firstText = lines
    .map((line) => cleanMarkdownInline(line.trim()))
    .find((line) => line && !isMarkdownDivider(line) && !line.startsWith('|'));

  return firstText || '전체 흐름 리포트';
}

function markdownHeadingTitle(line: string): string | undefined {
  const match = line.match(/^#{1,6}\s+(.+)$/);
  return match ? cleanHeadingTitle(match[1]) : undefined;
}

function numberedSectionTitle(line: string): string | undefined {
  const cleaned = cleanHeadingTitle(line);
  if (/^(?:#\s*)?\d+[\).]\s+/.test(cleaned)) {
    return cleaned.replace(/^#\s*/, '');
  }
  return undefined;
}

function cleanHeadingTitle(value: string): string {
  return cleanMarkdownInline(value)
    .replace(/^#+\s*/, '')
    .replace(/^\d+[\).]\s*/, '')
    .trim();
}

function cleanMarkdownInline(value: string): string {
  return value
    .replace(/^\s*[-*_]{3,}\s*$/, '')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/^#+\s*/, '')
    .trim();
}

function isMarkdownDivider(value: string): boolean {
  return /^[-*_]{3,}$/.test(value.trim());
}

function normalizeTitle(value: string): string {
  return cleanMarkdownInline(value).replace(/\s+/g, '').toLowerCase();
}

function splitLead(value: string): { label: string; body: string } | undefined {
  const match = value.match(/^([^:：]{2,36})[:：]\s*(.+)$/);
  if (!match) {
    return undefined;
  }
  return {
    label: match[1].trim(),
    body: match[2].trim()
  };
}

function gradeForTotal(total: number): { label: string; tone: string } {
  if (total >= 85) {
    return { label: 'A', tone: 'grade-a' };
  }
  if (total >= 70) {
    return { label: 'B', tone: 'grade-b' };
  }
  if (total >= 55) {
    return { label: 'C', tone: 'grade-c' };
  }
  return { label: 'D', tone: 'grade-d' };
}

function weakestAxis(scores: VibeScores): keyof VibeScores {
  return SCORE_KEYS.reduce((weakest, key) => (scores[key] < scores[weakest] ? key : weakest), SCORE_KEYS[0]);
}

function focusAdvice(key: keyof VibeScores): string {
  const advice: Record<keyof VibeScores, string> = {
    oneShot: '첫 요청에 성공 조건과 기대 산출물을 더 선명하게 묶어보세요.',
    context: '중간 전환점마다 현재 기준과 남은 작업을 짧게 재고정하세요.',
    control: '수정 금지 범위와 의사결정 기준을 먼저 선언하세요.',
    clarity: '파일 경로, 입력 예시, 검증 기준을 한 요청 안에 넣어보세요.'
  };
  return advice[key];
}

function radarChart(scores: VibeScores): string {
  const center = 60;
  const radius = 42;
  const values = [
    scores.oneShot,
    scores.context,
    scores.control,
    scores.clarity
  ].map((value) => (value / 25) * radius);
  const points = [
    `${center},${center - values[0]}`,
    `${center + values[1]},${center}`,
    `${center},${center + values[2]}`,
    `${center - values[3]},${center}`
  ].join(' ');

  return `
    <svg class="radar-chart" viewBox="0 0 120 120" role="img" aria-label="4축 점수 레이더 차트">
      <polygon class="radar-grid" points="60,18 102,60 60,102 18,60"></polygon>
      <polygon class="radar-grid inner" points="60,34 86,60 60,86 34,60"></polygon>
      <line x1="60" y1="18" x2="60" y2="102"></line>
      <line x1="18" y1="60" x2="102" y2="60"></line>
      <polygon class="radar-value" points="${points}"></polygon>
      <text x="60" y="12">원샷</text>
      <text x="105" y="63">맥락</text>
      <text x="60" y="116">제어</text>
      <text x="15" y="63">선명</text>
    </svg>
  `;
}

function smellCards(smells: string[]): string {
  return `
    <div class="smell-list">
      ${smells.slice(0, 4).map((smell, index) => `
        <div class="smell-item">
          <span>${index + 1}</span>
          <p>${escapeHtml(smell)}</p>
        </div>
      `).join('')}
    </div>
  `;
}

function examplesGrid(goodExamples: string[], badExamples: string[]): string {
  if (goodExamples.length === 0 && badExamples.length === 0) {
    return '<p class="report-empty">무료 초안 또는 AI 평가 후 예시가 표시됩니다.</p>';
  }

  return `
    <div class="example-grid">
      <div class="example-box bad">
        <b>Bad</b>
        ${actionList(badExamples.length > 0 ? badExamples.slice(0, 2) : ['아쉬운 예시는 아직 없습니다.'])}
      </div>
      <div class="example-box good">
        <b>Good</b>
        ${actionList(goodExamples.length > 0 ? goodExamples.slice(0, 2) : ['좋은 예시는 아직 없습니다.'])}
      </div>
    </div>
  `;
}

function actionList(items: string[]): string {
  return `<ul class="report-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`;
}

function sectionIcon(title: string): string {
  if (title.includes('요약')) {
    return '핵심';
  }
  if (title.includes('그래프') || title.includes('평균') || title.includes('비교')) {
    return '분석';
  }
  if (title.includes('신호') || title.includes('Smell')) {
    return '감지';
  }
  if (title.includes('액션') || title.includes('프롬프트')) {
    return '개선';
  }
  if (title.includes('세션')) {
    return '기록';
  }
  return '섹션';
}

function sectionClass(title: string): string {
  if (title.includes('신호') || title.includes('Smell')) {
    return 'warn';
  }
  if (title.includes('액션') || title.includes('프롬프트')) {
    return 'accent';
  }
  if (title.includes('그래프') || title.includes('평균') || title.includes('비교')) {
    return 'analysis';
  }
  return '';
}
