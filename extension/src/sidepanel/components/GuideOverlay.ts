export function GuideOverlay(open: boolean): string {
  return `
    <section class="guide-overlay${open ? '' : ' is-hidden'}"${open ? '' : ' hidden'}>
      <div class="guide-dialog" role="dialog" aria-modal="true" aria-label="VibeGraph 사용 가이드">
        <div class="guide-head">
          <h2>VibeGraph 사용 가이드</h2>
          <button class="ghost small" data-action="close-guide">닫기</button>
        </div>
        <div class="guide-slides">
          <article class="guide-slide" data-guide-slide="capture">
            <span>1</span>
            <h3>대화 캡처</h3>
            <p>Claude, ChatGPT, Gemini에서 작업이 끝나면 현재 대화 캡처를 누릅니다.</p>
          </article>
          <article class="guide-slide" data-guide-slide="score">
            <span>2</span>
            <h3>점수 만들기</h3>
            <p>직접 버튼을 고르거나 무료 초안 생성을 눌러 참고용 점수와 리포트를 먼저 만들 수 있습니다.</p>
          </article>
          <article class="guide-slide" data-guide-slide="prompt">
            <span>3</span>
            <h3>AI 결과 반영</h3>
            <p>더 정확한 판단이 필요하면 AI 평가 프롬프트를 복사해 대화창에 붙여넣고, 나온 JSON을 다시 VibeGraph에 붙여넣습니다.</p>
          </article>
          <article class="guide-slide" data-guide-slide="save">
            <span>4</span>
            <h3>저장 확정</h3>
            <p>제목, 메모, 점수, 리포트 초안은 수정정보 저장을 눌러야 브라우저 로컬 기록에 반영됩니다.</p>
          </article>
        </div>
      </div>
    </section>
  `;
}
