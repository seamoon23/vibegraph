import './styles.css';
import { parseAiReportResult } from '../core/aiResult.js';
import { buildLocalReportDraft, type VibeReportDraft } from '../core/autoReport.js';
import { buildLocalOverallReport } from '../core/overallReport.js';
import { buildAllSessionsReportPrompt, buildReportPrompt } from '../core/promptBuilder.js';
import { clampScore, normalizeScores } from '../core/scoring.js';
import { exportAllSessionsJson, exportSessionJson } from '../core/exportJson.js';
import { exportSessionMarkdown } from '../core/exportMarkdown.js';
import { makeSessionId, nowIso } from '../core/date.js';
import {
  deleteSession,
  loadSessions,
  loadSettings,
  saveSession,
  saveSettings
} from '../core/storage.js';
import type { CaptureResponse, ExtensionSettings, SessionSource, VibeScores, VibeSession } from '../core/types.js';
import { CapturePanel } from './components/CapturePanel.js';
import { EmptyState } from './components/EmptyState.js';
import { ErrorState } from './components/ErrorState.js';
import { ExportPanel, type OverallReportMode, type SelectedEvalMode } from './components/ExportPanel.js';
import { GuideOverlay } from './components/GuideOverlay.js';
import { OnboardingCard } from './components/OnboardingCard.js';
import { PrivacyNotice } from './components/PrivacyNotice.js';
import { SessionList } from './components/SessionList.js';
import { escapeHtml } from './components/html.js';

type Toast = {
  tone: 'info' | 'error';
  text: string;
};

type MainTab = 'sessions' | 'manage' | 'session-report' | 'overall-report';

export class App {
  private sessions: VibeSession[] = [];
  private settings: ExtensionSettings = { onboardingDismissed: false, privacyNoticeCollapsed: true };
  private selectedId: string | undefined;
  private toast: Toast | undefined;
  private captureError: string | undefined;
  private guideOpen = false;
  private dirtyIds = new Set<string>();
  private selectedEvalMode: SelectedEvalMode = 'manual';
  private overallReportMode: OverallReportMode = 'local';
  private activeTab: MainTab = 'overall-report';
  private readonly githubUrl = 'https://github.com/seamoon23/vibegraph';

  constructor(private readonly root: HTMLElement) {}

  async mount(): Promise<void> {
    this.sessions = await loadSessions();
    this.settings = await loadSettings();
    this.selectedId = undefined;
    this.render();
  }

  private selectedSession(): VibeSession | undefined {
    return this.sessions.find((session) => session.id === this.selectedId);
  }

  private render(): void {
    const selected = this.selectedSession();
    this.root.innerHTML = `
      <main class="app">
        <header class="topbar">
          <div>
            <h1 class="brand">VibeGraph</h1>
            <p class="subtitle">AI 작업 대화를 로컬에 기록합니다.</p>
          </div>
        </header>
        ${this.settings.onboardingDismissed ? '' : OnboardingCard()}
        ${this.toast ? `<div class="toast ${this.toast.tone === 'error' ? 'error' : ''}">${escapeHtml(this.toast.text)}</div>` : ''}
        ${CapturePanel()}
        ${this.selectedStrip(selected)}
        ${this.captureError ? ErrorState(this.captureError) : ''}
        ${this.tabBar()}
        <div class="layout">
          ${this.tabContent(selected)}
        </div>
        ${PrivacyNotice(this.settings.privacyNoticeCollapsed)}
        ${this.saveDock(selected)}
        ${GuideOverlay(this.guideOpen)}
      </main>
    `;
    this.bindEvents();
  }

  private tabBar(): string {
    return `
      <nav class="main-tabs" aria-label="VibeGraph 화면 전환">
        <button class="${this.activeTab === 'sessions' ? 'active' : ''}" data-tab="sessions">세션목록</button>
        <button class="${this.activeTab === 'manage' ? 'active' : ''}" data-tab="manage">대화 관리</button>
        <button class="${this.activeTab === 'session-report' ? 'active' : ''}" data-tab="session-report">개별 리포트</button>
        <button class="${this.activeTab === 'overall-report' ? 'active' : ''}" data-tab="overall-report">전체 리포트</button>
      </nav>
    `;
  }

  private tabContent(selected: VibeSession | undefined): string {
    const overallReportMarkdown =
      this.settings.overallReportMarkdown ??
      (this.sessions.length > 0 ? buildLocalOverallReport(this.sessions) : undefined);

    if (this.activeTab === 'sessions') {
      return `
        ${SessionList(this.sessions, this.selectedId, this.dirtyIds)}
        ${selected ? '' : EmptyState(this.sessions.length)}
      `;
    }

    if (this.activeTab === 'manage') {
      return `
        ${selected ? this.editor(selected, this.dirtyIds.has(selected.id)) : EmptyState(this.sessions.length)}
      `;
    }

    if (this.activeTab === 'session-report') {
      return ExportPanel({
        view: 'session',
        session: selected,
        sessionCount: this.sessions.length,
        selectedEvalMode: this.selectedEvalMode,
        overallReportMode: this.overallReportMode,
        overallReportMarkdown,
        overallReportUpdatedAt: this.settings.overallReportUpdatedAt,
        githubUrl: this.githubUrl
      });
    }

    return ExportPanel({
      view: 'overall',
      session: selected,
      sessionCount: this.sessions.length,
      selectedEvalMode: this.selectedEvalMode,
      overallReportMode: this.overallReportMode,
      overallReportMarkdown,
      overallReportUpdatedAt: this.settings.overallReportUpdatedAt,
      githubUrl: this.githubUrl
    });
  }

  private saveDock(session: VibeSession | undefined): string {
    if (!session) {
      return '';
    }

    const dirty = this.dirtyIds.has(session.id);
    return `
      <div class="save-dock ${dirty ? 'dirty' : 'clean'}">
        <div>
          <strong>${dirty ? '저장 전 변경사항 있음' : '저장됨'}</strong>
          <span>${dirty ? '새로고침하면 반영 전 값으로 돌아갈 수 있어요.' : '점수와 리포트를 바꾸면 여기에 저장 안내가 표시됩니다.'}</span>
        </div>
        <button class="primary" data-action="save-session"${dirty ? '' : ' disabled'}>저장</button>
      </div>
    `;
  }

  private selectedStrip(session: VibeSession | undefined): string {
    if (!session) {
      return '';
    }

    const total = session.scores
      ? Object.values(session.scores).reduce((sum, score) => sum + score, 0)
      : undefined;
    const score = total === undefined ? '점수 없음' : `${total}/100`;

    return `
      <aside class="selected-strip" aria-label="선택된 세션">
        <div>
          <span>선택됨</span>
          <strong>${escapeHtml(session.task || session.title || '제목 없음')}</strong>
          <p>${escapeHtml(session.source)} · 메시지 ${session.messages.length}개 · ${escapeHtml(session.capturedAt.slice(0, 10))}</p>
        </div>
        <b>${score}</b>
      </aside>
    `;
  }

  private editor(session: VibeSession, dirty: boolean): string {
    const messages = session.messages
      .slice(0, 6)
      .map((message) => `<p><b>${escapeHtml(message.role)}:</b> ${escapeHtml(message.text)}</p>`)
      .join('');

    return `
      <section class="panel">
        <div class="session-info-head">
          <h2>세션 정보</h2>
          <span>최초 캡처 ${escapeHtml(session.capturedAt.slice(0, 16).replace('T', ' '))}</span>
        </div>
        <div class="form-grid">
          <label>제목
            <input data-field="title" value="${escapeHtml(session.title)}" />
          </label>
          <label>대화 서비스
            <select data-field="source">
              ${sourceOptions(session.source)}
            </select>
          </label>
          <label>대화 링크
            <input data-field="url" value="${escapeHtml(session.url)}" placeholder="https://..." />
          </label>
          <label>프로젝트
            <input data-field="project" value="${escapeHtml(session.project)}" placeholder="vibegraph" />
          </label>
          <label>작업명
            <input data-field="task" value="${escapeHtml(session.task)}" placeholder="Chrome Extension MVP" />
          </label>
          <label>태그
            <input data-field="tags" value="${escapeHtml(session.tags.join(', '))}" placeholder="chrome, mvp" />
          </label>
          <label>메모
            <textarea data-field="notes">${escapeHtml(session.notes ?? '')}</textarea>
          </label>
          <label>Prompt Smell / 개선 신호
            <input data-field="promptSmells" value="${escapeHtml((session.promptSmells ?? []).join(', '))}" placeholder="scope drift" />
          </label>
          <div>
            <p class="muted">대화 서비스: ${escapeHtml(session.source)} · 메시지 ${session.messages.length}개</p>
            <div class="conversation-preview">${messages || '<p>캡처된 메시지가 없습니다.</p>'}</div>
          </div>
          <details class="conversation-edit"${session.messages.length === 0 ? ' open' : ''}>
            <summary>대화 원문 직접 입력</summary>
            <label>다른 곳의 대화를 가져온 경우 여기에 붙여넣으세요.
              <textarea data-field="conversationText" placeholder="대화 내용을 붙여넣으면 메시지 1개짜리 직접입력 기록으로 저장됩니다.">${escapeHtml(conversationText(session))}</textarea>
            </label>
          </details>
          <div class="save-row">
            <button class="primary" data-action="save-session"${dirty ? '' : ' disabled'}>수정정보 저장</button>
            <p class="save-help" data-dirty-state>
              ${dirty ? '저장 전 변경사항이 있습니다.' : '수정 후 저장 버튼을 눌러야 브라우저 로컬 기록에 반영됩니다.'}
            </p>
          </div>
        </div>
      </section>
    `;
  }

  private bindEvents(): void {
    this.root.querySelectorAll<HTMLElement>('[data-action]').forEach((element) => {
      element.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        void this.handleAction(element.dataset.action ?? '', element);
      });
    });

    this.root.querySelectorAll<HTMLElement>('[data-session-id]').forEach((element) => {
      element.addEventListener('click', () => {
        this.selectedId = element.dataset.sessionId;
        this.captureError = undefined;
        this.render();
      });
    });

    this.root.querySelectorAll<HTMLElement>('[data-tab]').forEach((element) => {
      element.addEventListener('click', () => {
        this.activeTab = parseMainTab(element.dataset.tab);
        this.render();
      });
    });

    this.root.querySelectorAll<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>('[data-field]').forEach((element) => {
      const eventName = element instanceof HTMLSelectElement ? 'change' : 'input';
      element.addEventListener(eventName, () => this.updateFieldDraft(element.dataset.field ?? '', element.value));
    });

    this.root.querySelectorAll<HTMLInputElement>('[data-score]').forEach((element) => {
      element.addEventListener('change', () => {
        this.updateScoreDraft(element.dataset.score as keyof VibeScores, element.value);
      });
    });

    this.root.querySelectorAll<HTMLElement>('[data-score-preset]').forEach((element) => {
      element.addEventListener('click', () => {
        const [key, value] = (element.dataset.scorePreset ?? '').split(':');
        this.updateScoreDraft(key as keyof VibeScores, value);
      });
    });
  }

  private async handleAction(action: string, element: HTMLElement): Promise<void> {
    if (action === 'dismiss-onboarding') {
      this.settings = { ...this.settings, onboardingDismissed: true };
      await saveSettings(this.settings);
      this.render();
      return;
    }

    if (action === 'toggle-privacy') {
      this.settings = {
        ...this.settings,
        privacyNoticeCollapsed: !this.settings.privacyNoticeCollapsed
      };
      await saveSettings(this.settings);
      this.render();
      return;
    }

    if (action === 'capture-current') {
      await this.captureCurrent();
      return;
    }

    if (action === 'manual-session') {
      await this.createManualSession();
      return;
    }

    if (action === 'open-guide') {
      this.guideOpen = true;
      this.render();
      return;
    }

    if (action === 'close-guide') {
      this.guideOpen = false;
      this.render();
      return;
    }

    if (action === 'save-session') {
      await this.saveSelected();
      return;
    }

    if (action === 'set-selected-eval-mode') {
      this.selectedEvalMode =
        element.dataset.evalMode === 'ai' ? 'ai' : element.dataset.evalMode === 'local' ? 'local' : 'manual';
      this.render();
      return;
    }

    if (action === 'set-overall-report-mode') {
      this.overallReportMode = element.dataset.overallMode === 'ai' ? 'ai' : 'local';
      this.render();
      return;
    }

    if (action === 'score-selected-local') {
      this.scoreSelectedLocal();
      return;
    }

    if (action === 'score-all-local') {
      this.scoreAllLocal();
      return;
    }

    if (action === 'copy-prompt') {
      await this.copyPrompt();
      return;
    }

    if (action === 'copy-all-prompt') {
      await this.copyAllPrompt();
      return;
    }

    if (action === 'generate-overall-local') {
      await this.generateOverallLocal();
      return;
    }

    if (action === 'apply-overall-report') {
      await this.applyOverallReport();
      return;
    }

    if (action === 'apply-ai-result') {
      this.applyAiResult();
      return;
    }

    if (action === 'export-md') {
      this.exportMarkdown();
      return;
    }

    if (action === 'export-json') {
      this.exportJson();
      return;
    }

    if (action === 'backup-json') {
      this.download('vibegraph-sessions.json', exportAllSessionsJson(this.sessions), 'application/json');
      return;
    }

    if (action === 'export-overall-md') {
      this.exportOverallMarkdown();
      return;
    }

    if (action === 'delete-session') {
      await this.removeSession(element.dataset.deleteSessionId);
    }
  }

  private async captureCurrent(): Promise<void> {
    this.toast = { tone: 'info', text: '캡처 중입니다.' };
    this.captureError = undefined;
    this.render();

    const response = await chrome.runtime.sendMessage<CaptureResponse>({
      type: 'VIBEGRAPH_CAPTURE_ACTIVE_TAB'
    });

    if (!response.ok) {
      this.toast = {
        tone: 'error',
        text: response.unsupported ? '아직 지원하지 않는 페이지예요.' : '캡처에 실패했습니다.'
      };
      this.captureError = response.reason;
      this.render();
      return;
    }

    const timestamp = nowIso();
    const session: VibeSession = {
      ...response.conversation,
      id: makeSessionId(response.conversation.source, response.conversation.capturedAt),
      project: '',
      task: response.conversation.title,
      tags: [],
      createdAt: timestamp,
      updatedAt: timestamp,
      notes: '',
      promptSmells: []
    };

    this.sessions = await saveSession(session);
    this.selectedId = session.id;
    this.activeTab = 'manage';
    this.dirtyIds.delete(session.id);
    this.toast = { tone: 'info', text: '캡처 완료. 대화관리 탭에서 제목과 원문을 확인해 보세요.' };
    this.render();
  }

  private async createManualSession(): Promise<void> {
    const timestamp = nowIso();
    const session: VibeSession = {
      id: makeSessionId('manual', timestamp),
      source: 'manual',
      title: '직접 입력',
      url: '',
      project: '',
      task: '',
      tags: [],
      createdAt: timestamp,
      updatedAt: timestamp,
      capturedAt: timestamp,
      messages: [],
      notes: '',
      promptSmells: []
    };

    this.sessions = await saveSession(session);
    this.selectedId = session.id;
    this.activeTab = 'manage';
    this.captureError = undefined;
    this.dirtyIds.delete(session.id);
    this.toast = { tone: 'info', text: '직접입력 기록을 만들었습니다. 대화 서비스와 원문을 채워 보세요.' };
    this.render();
  }

  private updateFieldDraft(field: string, value: string): void {
    const selected = this.selectedSession();
    if (!selected) {
      return;
    }

    if (field === 'source') {
      selected.source = parseSource(value);
    } else if (field === 'conversationText') {
      selected.messages = value.trim()
        ? [{ role: 'unknown', text: value.trim(), order: 1 }]
        : [];
    } else if (field === 'tags') {
      selected.tags = splitList(value);
    } else if (field === 'promptSmells') {
      selected.promptSmells = splitList(value);
    } else if (field === 'title' || field === 'project' || field === 'task' || field === 'notes' || field === 'url') {
      selected[field] = value.trim();
    }

    this.markDirty(selected.id);
  }

  private updateScoreDraft(key: keyof VibeScores, value: string): void {
    const selected = this.selectedSession();
    if (!selected || !key) {
      return;
    }

    selected.scores = normalizeScores({
      ...(selected.scores ?? {}),
      [key]: clampScore(value)
    });
    this.markDirty(selected.id);
    this.render();
  }

  private async saveSelected(): Promise<void> {
    const selected = this.selectedSession();
    if (!selected) {
      return;
    }

    selected.updatedAt = nowIso();
    this.sessions = await saveSession(selected);
    this.selectedId = selected.id;
    this.dirtyIds.delete(selected.id);
    this.toast = { tone: 'info', text: '수정사항을 저장했습니다.' };
    this.render();
  }

  private scoreSelectedLocal(): void {
    const selected = this.selectedSession();
    if (!selected) {
      return;
    }

    this.applyReportDraft(selected, buildLocalReportDraft(selected));
    this.markDirty(selected.id);
    this.toast = { tone: 'info', text: '무료 초안을 반영했습니다. 확인 후 수정정보 저장을 눌러 확정하세요.' };
    this.render();
  }

  private scoreAllLocal(): void {
    if (this.sessions.length === 0) {
      return;
    }

    this.sessions = this.sessions.map((session) => {
      const next = { ...session };
      this.applyReportDraft(next, buildLocalReportDraft(next));
      this.dirtyIds.add(next.id);
      return next;
    });
    this.toast = { tone: 'info', text: '전체 세션에 무료 초안을 만들었습니다. 각 세션 확인 후 저장하세요.' };
    this.render();
  }

  private async copyPrompt(): Promise<void> {
    const selected = this.selectedSession();
    if (!selected) {
      return;
    }

    await navigator.clipboard.writeText(buildReportPrompt(selected));
    this.toast = {
      tone: 'info',
      text: 'AI 평가 프롬프트를 복사했습니다. AI 대화창 입력창에 붙여넣고, 나온 JSON을 아래 칸에 다시 붙여넣으세요.'
    };
    this.render();
  }

  private async copyAllPrompt(): Promise<void> {
    if (this.sessions.length === 0) {
      return;
    }

    await navigator.clipboard.writeText(buildAllSessionsReportPrompt(this.sessions));
    this.toast = {
      tone: 'info',
      text: '전체 리포트 프롬프트를 복사했습니다. AI 대화창에 붙여넣고, 나온 Markdown을 전체 흐름 리포트 칸에 붙여넣으세요.'
    };
    this.render();
  }

  private async generateOverallLocal(): Promise<void> {
    this.settings = {
      ...this.settings,
      overallReportMarkdown: buildLocalOverallReport(this.sessions),
      overallReportUpdatedAt: nowIso()
    };
    await saveSettings(this.settings);
    this.toast = { tone: 'info', text: '전체 흐름 무료 요약을 만들었습니다.' };
    this.render();
  }

  private async applyOverallReport(): Promise<void> {
    const raw = this.root.querySelector<HTMLTextAreaElement>('[data-overall-ai-report]')?.value.trim() ?? '';
    if (!raw) {
      this.toast = { tone: 'error', text: 'AI가 작성한 전체 리포트 Markdown을 먼저 붙여넣어 주세요.' };
      this.render();
      return;
    }

    this.settings = {
      ...this.settings,
      overallReportMarkdown: raw,
      overallReportUpdatedAt: nowIso()
    };
    await saveSettings(this.settings);
    this.toast = { tone: 'info', text: '전체 흐름 AI 리포트를 저장했습니다.' };
    this.render();
  }

  private applyAiResult(): void {
    const selected = this.selectedSession();
    if (!selected) {
      return;
    }

    const raw = this.root.querySelector<HTMLTextAreaElement>('[data-ai-result]')?.value.trim() ?? '';
    if (!raw) {
      this.toast = { tone: 'error', text: 'AI가 준 JSON을 먼저 붙여넣어 주세요.' };
      this.render();
      return;
    }

    try {
      this.applyReportDraft(selected, parseAiReportResult(raw));
      this.markDirty(selected.id);
      this.toast = { tone: 'info', text: 'AI 응답을 반영했습니다. 수정정보 저장을 눌러 확정하세요.' };
    } catch (error) {
      this.toast = {
        tone: 'error',
        text: error instanceof Error ? `AI 응답을 읽지 못했습니다: ${error.message}` : 'AI 응답을 읽지 못했습니다.'
      };
    }

    this.render();
  }

  private applyReportDraft(session: VibeSession, draft: VibeReportDraft): void {
    session.summary = draft.summary;
    session.scores = draft.scores;
    session.promptSmells = draft.promptSmells;
    session.goodExamples = draft.goodExamples;
    session.badExamples = draft.badExamples;
    session.nextActions = draft.nextActions;
  }

  private exportMarkdown(): void {
    const selected = this.selectedSession();
    if (selected) {
      this.download(`${safeFileName(selected.task || selected.title)}.md`, exportSessionMarkdown(selected), 'text/markdown');
    }
  }

  private exportJson(): void {
    const selected = this.selectedSession();
    if (selected) {
      this.download(`${safeFileName(selected.task || selected.title)}.json`, exportSessionJson(selected), 'application/json');
    }
  }

  private exportOverallMarkdown(): void {
    if (this.settings.overallReportMarkdown) {
      this.download('vibegraph-overall-report.md', this.settings.overallReportMarkdown, 'text/markdown');
    }
  }

  private async removeSession(sessionId: string | undefined): Promise<void> {
    const id = sessionId || this.selectedId;
    if (!id) {
      return;
    }

    const target = this.sessions.find((session) => session.id === id);
    const label = target?.task || target?.title || '이 기록';
    if (!window.confirm(`"${label}" 기록을 브라우저 로컬 저장소에서 삭제할까요?`)) {
      return;
    }

    const wasSelected = id === this.selectedId;
    this.sessions = await deleteSession(id);
    this.dirtyIds.delete(id);
    this.selectedId = wasSelected ? undefined : this.selectedId;
    this.toast = { tone: 'info', text: '세션 기록을 삭제했습니다.' };
    this.render();
  }

  private markDirty(sessionId: string): void {
    this.dirtyIds.add(sessionId);
    const selected = this.selectedSession();
    if (selected?.id !== sessionId) {
      return;
    }

    this.root.querySelectorAll<HTMLButtonElement>('[data-action="save-session"]').forEach((button) => {
      button.removeAttribute('disabled');
    });
    this.root.querySelectorAll<HTMLElement>('[data-dirty-state]').forEach((state) => {
      state.textContent = '저장 전 변경사항이 있습니다.';
    });
    this.root.querySelectorAll<HTMLElement>('.save-dock').forEach((dock) => {
      dock.classList.remove('clean');
      dock.classList.add('dirty');
      dock.querySelector('strong')?.replaceChildren(document.createTextNode('저장 전 변경사항 있음'));
      dock.querySelector('span')?.replaceChildren(document.createTextNode('새로고침하면 반영 전 값으로 돌아갈 수 있어요.'));
    });
  }

  private download(filename: string, content: string, mime: string): void {
    const blob = new Blob([content], { type: `${mime};charset=utf-8` });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }

}

function splitList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function sourceOptions(selected: SessionSource): string {
  const sources: Array<{ value: SessionSource; label: string }> = [
    { value: 'claude', label: 'Claude' },
    { value: 'chatgpt', label: 'ChatGPT' },
    { value: 'gemini', label: 'Gemini' },
    { value: 'manual', label: '직접입력' },
    { value: 'unknown', label: '기타 / 알 수 없음' }
  ];

  return sources
    .map((source) => {
      const selectedAttribute = source.value === selected ? ' selected' : '';
      return `<option value="${source.value}"${selectedAttribute}>${escapeHtml(source.label)}</option>`;
    })
    .join('');
}

function parseSource(value: string): SessionSource {
  if (value === 'claude' || value === 'chatgpt' || value === 'gemini' || value === 'manual') {
    return value;
  }
  return 'unknown';
}

function conversationText(session: VibeSession): string {
  if (session.messages.length === 1 && session.messages[0].role === 'unknown') {
    return session.messages[0].text;
  }

  return session.messages
    .map((message) => `${message.role}: ${message.text}`)
    .join('\n\n');
}

function parseMainTab(value: string | undefined): MainTab {
  if (value === 'sessions' || value === 'manage' || value === 'session-report' || value === 'overall-report') {
    return value;
  }
  return 'overall-report';
}

function safeFileName(value: string): string {
  return (
    value
      .toLowerCase()
      .replace(/[^a-z0-9가-힣_-]+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 60) || 'vibegraph-session'
  );
}
