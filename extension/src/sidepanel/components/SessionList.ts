import type { VibeSession } from '../../core/types.js';
import { compactDateTime } from '../../core/date.js';
import { escapeHtml } from './html.js';

export function SessionList(
  sessions: VibeSession[],
  selectedId: string | undefined,
  dirtyIds: ReadonlySet<string> = new Set()
): string {
  if (sessions.length === 0) {
    return '';
  }

  const items = sessions
    .map((session) => {
      const active = session.id === selectedId ? ' active' : '';
      const dirty = dirtyIds.has(session.id);
      return `
        <div class="session-item${active}">
          <button class="session-button" data-session-id="${escapeHtml(session.id)}">
            <span class="session-title">${escapeHtml(session.task || session.title || '제목 없음')}</span>
            <span class="session-meta">${escapeHtml(session.source)} · 메시지 ${session.messages.length}개 · ${escapeHtml(compactDateTime(session.updatedAt))}</span>
            ${dirty ? '<span class="session-dirty">저장 전</span>' : ''}
          </button>
          <button
            class="session-delete"
            data-action="delete-session"
            data-delete-session-id="${escapeHtml(session.id)}"
            title="브라우저 로컬에 저장된 이 기록만 삭제합니다."
            aria-label="세션 삭제"
          >
            삭제
          </button>
        </div>
      `;
    })
    .join('');

  return `
    <section class="panel">
      <h2>세션 목록</h2>
      <div class="session-list">${items}</div>
    </section>
  `;
}
