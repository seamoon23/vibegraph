import { escapeHtml } from './html.js';

export function ErrorState(message: string): string {
  return `
    <section class="error">
      <h2>대화를 찾지 못했어요</h2>
      <p>${escapeHtml(message)}</p>
      <p>페이지를 새로고침하거나 대화가 보이는 상태에서 다시 시도해 주세요. 제목과 메모만으로 수동 기록도 만들 수 있습니다.</p>
    </section>
  `;
}
