import { CapturePanel } from './CapturePanel.js';
import { EmptyState } from './EmptyState.js';
import { ExportPanel } from './ExportPanel.js';
import { GuideOverlay } from './GuideOverlay.js';
import { PrivacyNotice } from './PrivacyNotice.js';
import { ScoreEditor } from './ScoreEditor.js';
import { SessionList } from './SessionList.js';
import type { VibeSession } from '../../core/types.js';

function assertIncludes(actual: string, expected: string, message: string): void {
  if (!actual.includes(expected)) {
    throw new Error(`${message}. Missing ${JSON.stringify(expected)} in ${JSON.stringify(actual)}`);
  }
}

function assertNotIncludes(actual: string, unexpected: string, message: string): void {
  if (actual.includes(unexpected)) {
    throw new Error(`${message}. Unexpected ${JSON.stringify(unexpected)} in ${JSON.stringify(actual)}`);
  }
}

const session: VibeSession = {
  id: 'session-1',
  source: 'claude',
  title: 'Claude code work',
  url: 'https://claude.ai/chat/abc',
  project: '',
  task: 'Claude code work',
  tags: [],
  createdAt: '2026-07-05T03:10:00.000Z',
  updatedAt: '2026-07-05T03:10:00.000Z',
  capturedAt: '2026-07-05T03:10:00.000Z',
  messages: [{ role: 'unknown', text: 'long captured message', order: 1 }],
  summary: '선택 세션 요약',
  scores: { oneShot: 18, context: 17, control: 16, clarity: 19 },
  promptSmells: ['초기 요구사항이 늦게 정리됨'],
  goodExamples: ['완료 기준을 명확히 적음'],
  badExamples: ['버튼 의미가 불명확함'],
  nextActions: ['다음에는 완료 기준을 먼저 적기']
};

const collapsedNotice = PrivacyNotice(true);
assertIncludes(collapsedNotice, 'data-action="toggle-privacy"', 'collapsed privacy notice has toggle');
assertIncludes(collapsedNotice, '개인정보 안내', 'collapsed privacy notice keeps heading');
assertNotIncludes(collapsedNotice, '서버로 대화를 전송하지 않습니다', 'collapsed privacy notice hides body');

const expandedNotice = PrivacyNotice(false);
assertIncludes(expandedNotice, '서버로 대화를 전송하지 않습니다', 'expanded privacy notice shows body');

const capturedPanel = CapturePanel();
assertIncludes(capturedPanel, 'data-action="capture-current"', 'capture panel keeps capture action');
assertIncludes(capturedPanel, 'data-action="manual-session"', 'capture panel exposes direct input action');
assertIncludes(capturedPanel, '직접 입력', 'capture panel renames manual record to direct input');
assertNotIncludes(capturedPanel, 'jump-scores', 'capture panel no longer shows score jump action');
assertNotIncludes(capturedPanel, '캡처 완료', 'capture panel does not repeat captured session text under buttons');
assertNotIncludes(capturedPanel, '아직 평가 전입니다', 'capture panel keeps the button area compact before capture');

const scoreEditor = ScoreEditor(session.scores);
assertIncludes(scoreEditor, 'data-action="open-guide"', 'score editor exposes guide action');
assertIncludes(scoreEditor, 'data-score-preset="oneShot:0"', 'score editor exposes low one-shot preset');
assertIncludes(scoreEditor, 'data-score-preset="clarity:25"', 'score editor exposes high clarity preset');
assertIncludes(scoreEditor, '<summary>직접 숫자 입력</summary>', 'score editor separates manual input');
assertIncludes(scoreEditor, '직접 판단할 때만', 'score editor explains optional manual scoring');
assertIncludes(scoreEditor, '저장 전까지는 임시 변경', 'score editor explains explicit save behavior');

const sessionList = SessionList([session], session.id, new Set([session.id]));
assertIncludes(sessionList, 'data-delete-session-id="session-1"', 'session list owns delete action');
assertIncludes(sessionList, '브라우저 로컬에 저장된 이 기록만 삭제합니다', 'session list explains delete scope');
assertIncludes(sessionList, '메시지 1개', 'session list shows message count per conversation');
assertIncludes(sessionList, '저장 전', 'session list marks unsaved sessions');

const noAutoSelected = EmptyState(2);
assertIncludes(noAutoSelected, '세션을 선택하세요', 'empty state asks user to explicitly select a saved session');
assertIncludes(noAutoSelected, '이전 기록을 자동으로 선택하지 않습니다', 'empty state explains no auto-selection');

const overallMarkdown = [
  '# 전체 흐름 리포트',
  '',
  '## 요약',
  '',
  '- 전체 세션: 3개',
  '- 평균 점수: 68.5 / 100',
  '- 가장 약한 축: 원샷 성공률',
  '',
  '## 4축 평균',
  '',
  '- 원샷 성공률: 14.5 / 25',
  '- 컨텍스트 유지력: 19.8 / 25',
  '',
  '## 점수 비교표',
  '',
  '| 항목 | 평균 | 해석 |',
  '| --- | ---: | --- |',
  '| 원샷 성공률 | 14.5/25 | 보완 필요 |',
  '',
  '## 반복 개선 신호',
  '',
  '- Missing Context (2회)',
  '',
  '## 다음 액션',
  '',
  '- 첫 요청에 완료 기준을 함께 적기',
  '',
  '## 최근 세션',
  '',
  '- Claude code work: 70 / 100'
].join('\n');

const localExportPanel = ExportPanel({
  view: 'session',
  session,
  sessionCount: 1,
  selectedEvalMode: 'local',
  overallReportMode: 'local',
  overallReportMarkdown: overallMarkdown,
  overallReportUpdatedAt: '2026-07-05T03:30:00.000Z',
  githubUrl: 'https://github.com/seamoon23/vibegraph'
});
assertIncludes(localExportPanel, 'data-eval-mode="manual"', 'export panel exposes manual scoring mode');
assertIncludes(localExportPanel, 'data-eval-mode="local"', 'export panel exposes free draft scoring mode');
assertIncludes(localExportPanel, 'data-eval-mode="ai"', 'export panel exposes AI scoring mode');
assertIncludes(localExportPanel, '더미데이터가 아니라', 'free draft explains it is not dummy data');
assertIncludes(localExportPanel, 'AI 의미판단이 아니므로', 'free draft explains its limitation');
assertIncludes(localExportPanel, 'report-hero', 'selected report has visual hero summary');
assertIncludes(localExportPanel, 'axis-score-row', 'selected report shows score comparison bars');
assertIncludes(localExportPanel, 'radar-chart', 'selected report shows radar chart');
assertIncludes(localExportPanel, 'smell-item', 'selected report splits prompt smells into cards');
assertIncludes(localExportPanel, 'example-grid', 'selected report shows good/bad examples visually');

const manualExportPanel = ExportPanel({
  view: 'session',
  session,
  sessionCount: 1,
  selectedEvalMode: 'manual',
  overallReportMode: 'local',
  githubUrl: 'https://github.com/seamoon23/vibegraph'
});
assertIncludes(manualExportPanel, '직접 판단하고 싶은 경우만 열어 쓰세요', 'manual scoring is optional and collapsible by mode');

const exportPanel = ExportPanel({
  view: 'session',
  session,
  sessionCount: 1,
  selectedEvalMode: 'ai',
  overallReportMode: 'ai',
  overallReportMarkdown: overallMarkdown,
  overallReportUpdatedAt: '2026-07-05T03:30:00.000Z',
  githubUrl: 'https://github.com/seamoon23/vibegraph'
});
assertIncludes(exportPanel, '선택 세션 평가', 'export panel separates selected session evaluation');
assertIncludes(exportPanel, 'data-ai-result', 'export panel accepts pasted AI JSON');
assertIncludes(exportPanel, '붙여넣은 JSON으로 선택 리포트 갱신', 'export panel explains AI JSON apply action');
assertIncludes(exportPanel, '내보내기 / 추가설정', 'export panel moves export and CLI help into utility area');
assertIncludes(exportPanel, 'https://github.com/seamoon23/vibegraph', 'export panel links GitHub guidance');

const overallExportPanel = ExportPanel({
  view: 'overall',
  session,
  sessionCount: 1,
  selectedEvalMode: 'ai',
  overallReportMode: 'local',
  overallReportMarkdown: overallMarkdown,
  overallReportUpdatedAt: '2026-07-05T03:30:00.000Z',
  githubUrl: 'https://github.com/seamoon23/vibegraph'
});
assertIncludes(overallExportPanel, '전체 흐름 리포트', 'overall tab shows overall flow report');
assertIncludes(overallExportPanel, 'overall-hero', 'overall tab starts with a visual focus hero');
assertIncludes(overallExportPanel, 'overall-hero-bar', 'overall hero includes a score progress bar');
assertIncludes(overallExportPanel, 'overall-card', 'overall report markdown is split into visual cards');
assertIncludes(overallExportPanel, 'overall-kpi-grid', 'overall summary renders as KPI cards');
assertIncludes(overallExportPanel, 'overall-axis-row', 'overall axis averages render as bars');
assertIncludes(overallExportPanel, 'overall-compare-row', 'overall comparison table renders as rows');
assertNotIncludes(overallExportPanel, 'markdown-table-line', 'overall report avoids raw markdown table rendering when possible');
assertIncludes(overallExportPanel, 'data-action="generate-overall-local"', 'overall tab exposes local overall report');
assertIncludes(overallExportPanel, 'data-action="score-all-local"', 'overall tab exposes per-session bulk local draft scoring');

const overallAiPanel = ExportPanel({
  view: 'overall',
  session,
  sessionCount: 1,
  selectedEvalMode: 'ai',
  overallReportMode: 'ai',
  overallReportMarkdown: overallMarkdown,
  overallReportUpdatedAt: '2026-07-05T03:30:00.000Z',
  githubUrl: 'https://github.com/seamoon23/vibegraph'
});
assertIncludes(overallAiPanel, 'data-action="copy-all-prompt"', 'overall tab exposes all-session report prompt');
assertIncludes(overallAiPanel, 'data-overall-ai-report', 'overall tab accepts pasted overall AI report');
assertIncludes(overallAiPanel, '붙여넣은 Markdown을 전체 흐름 리포트로 보기', 'overall tab applies overall AI Markdown');

const aiOverallPanel = ExportPanel({
  view: 'overall',
  session,
  sessionCount: 1,
  selectedEvalMode: 'ai',
  overallReportMode: 'ai',
  overallReportMarkdown: [
    '전체 흐름 리포트',
    '',
    '---',
    '',
    '### 1. 종합 패턴 (Overall Pattern)',
    '',
    '**AI 예비 유지의 생산성 병목 관리 단계:** 3대 메이저 AI Pro 버전을 모두 활용하며, Claude Code와 VS Code 확장기능을 실무에 적극적으로 씁니다.',
    '',
    '### 2. 반복되는 Prompt Smell',
    '',
    '- Missing Context가 여러 세션에서 반복됩니다.',
    '- Scope Creep이 후반부에 나타납니다.',
    '',
    '### 3. 권장 액션',
    '',
    '- 시작 프롬프트에 완료 기준을 먼저 적으세요.'
  ].join('\n'),
  overallReportUpdatedAt: '2026-07-05T03:31:00.000Z',
  githubUrl: 'https://github.com/seamoon23/vibegraph'
});
assertIncludes(aiOverallPanel, 'overall-narrative-item', 'AI freeform overall report renders prose as visual cards');
assertIncludes(aiOverallPanel, 'overall-signal-item', 'AI freeform prompt smells render as signal cards');
assertIncludes(aiOverallPanel, 'overall-action-item', 'AI freeform recommendations render as action cards');
assertNotIncludes(aiOverallPanel, '### 1.', 'AI freeform headings are not shown as raw markdown');
assertNotIncludes(aiOverallPanel, '---', 'AI freeform dividers are not shown as raw markdown');

const hiddenGuide = GuideOverlay(false);
assertIncludes(hiddenGuide, 'hidden', 'guide overlay is hidden when closed');
assertIncludes(hiddenGuide, 'is-hidden', 'guide overlay has explicit hidden class for CSS');

const visibleGuide = GuideOverlay(true);
assertIncludes(visibleGuide, 'data-guide-slide="capture"', 'guide overlay shows capture slide');
assertIncludes(visibleGuide, 'data-guide-slide="score"', 'guide overlay shows score slide');
assertIncludes(visibleGuide, 'data-guide-slide="prompt"', 'guide overlay shows prompt slide');
assertIncludes(visibleGuide, 'data-guide-slide="save"', 'guide overlay shows save slide');

console.log('ok - side panel components expose guided scoring, prompt flow, and usage guide');
