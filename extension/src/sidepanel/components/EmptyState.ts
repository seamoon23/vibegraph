export function EmptyState(sessionCount = 0): string {
  if (sessionCount > 0) {
    return `
      <section class="empty">
        <h2>세션을 선택하세요</h2>
        <p>왼쪽/위쪽 세션 목록에서 기록을 직접 선택하면 세션 정보와 리포트가 열립니다.</p>
        <p>처음 열 때는 이전 기록을 자동으로 선택하지 않습니다. 현재 대화인지 과거 기록인지 헷갈리지 않도록 비워 둡니다.</p>
      </section>
    `;
  }

  return `
    <section class="empty">
      <h2>아직 저장된 세션이 없습니다</h2>
      <p>Claude, ChatGPT, Gemini 대화창에서 현재 대화 캡처를 눌러 첫 기록을 만들어 보세요.</p>
    </section>
  `;
}
