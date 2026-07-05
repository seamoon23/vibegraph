import { App } from './App.js';

const root = document.querySelector<HTMLElement>('#app');

if (!root) {
  throw new Error('VibeGraph side panel root was not found.');
}

const app = new App(root);
app.mount().catch((error) => {
  root.innerHTML = `
    <main class="app">
      <section class="error">
        <h2>초기화에 실패했습니다</h2>
        <p>${error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.'}</p>
      </section>
    </main>
  `;
});
