export function PrivacyNotice(collapsed: boolean): string {
  const body = collapsed
    ? ''
    : `
      <div class="notice-body">
        <p>이 확장은 서버로 대화를 전송하지 않습니다.</p>
        <p>저장은 브라우저 로컬에만 이루어지고, 사용자가 버튼을 누른 대화만 캡처합니다.</p>
      </div>
    `;

  return `
    <section class="notice compact">
      <div class="notice-head">
        <h2>개인정보 안내</h2>
        <button class="ghost small" data-action="toggle-privacy">${collapsed ? '보기' : '접기'}</button>
      </div>
      ${body}
    </section>
  `;
}
