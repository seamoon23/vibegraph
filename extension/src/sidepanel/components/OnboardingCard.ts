export function OnboardingCard(): string {
  return `
    <section class="notice onboarding">
      <h2>VibeGraph에 오신 것을 환영합니다</h2>
      <ol>
        <li>Claude, ChatGPT, Gemini 대화창을 엽니다.</li>
        <li>현재 대화 캡처를 누릅니다.</li>
        <li>프로젝트, 태그, 4축 점수를 남깁니다.</li>
      </ol>
      <button class="secondary" data-action="dismiss-onboarding">시작하기</button>
    </section>
  `;
}
