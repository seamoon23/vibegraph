export function CapturePanel(): string {
  return `
    <section class="panel capture-panel">
      <div class="toolbar">
        <button class="primary" data-action="capture-current">현재 대화 캡처</button>
        <button class="ghost" data-action="manual-session">직접 입력</button>
      </div>
    </section>
  `;
}
