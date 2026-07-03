# Codex 작업 요청서: VibeGraph Chrome Extension MVP

## 작업 대상

Repository: `seamoon23/vibegraph`

기존 VibeGraph Python CLI 기능은 유지하고, 별도 `extension/` 하위 폴더에 Chrome Extension MVP를 추가한다.

이번 MVP는 Claude.ai / ChatGPT / Gemini 웹 대화창에서 사용자가 버튼을 눌러 현재 대화를 캡처하고, 프로젝트/작업명/태그/수동 점수를 기록한 뒤, Markdown/JSON Export와 VibeGraph 리포트 프롬프트 복사를 제공하는 **로컬 우선 Chrome 확장 프로그램**이다.

---

## 핵심 목표

```text
AI 웹 대화창
  → VibeGraph 사이드패널 열기
  → 현재 대화 캡처
  → 프로젝트/작업명/태그 입력
  → 4축 점수 입력
  → 리포트 프롬프트 복사 또는 Markdown/JSON 내보내기
```

---

## 중요한 원칙

1. 기존 Python CLI 기능을 깨지 말 것.
2. 기존 루트 구조를 과도하게 변경하지 말 것.
3. Chrome Extension은 Manifest V3 기준으로 작성할 것.
4. 원격 호스팅 JS 실행 금지. 모든 코드는 패키지 내부 번들로 포함할 것.
5. 서버/API 호출 없음.
6. 사용자가 명시적으로 누른 경우에만 현재 페이지 대화를 캡처할 것.
7. 개인정보 신뢰를 위해 “로컬 저장 / 외부 전송 없음” 문구와 UX를 반드시 포함할 것.
8. 한국어 UI를 기본으로 작성하되, 코드 구조는 추후 i18n 가능하게 분리할 것.
9. 고객친화적인 온보딩, 빈 상태, 오류 상태, 안내 문구를 포함할 것.
10. DOM 구조 변경에 취약할 수 있으므로 adapter 단위로 안전하게 분리할 것.

---

## 권장 폴더 구조

```text
extension/
  package.json
  tsconfig.json
  vite.config.ts
  manifest.json
  public/
    icons/
  src/
    background/
      serviceWorker.ts
    content/
      index.ts
      adapters/
        claude.ts
        chatgpt.ts
        gemini.ts
        common.ts
    sidepanel/
      index.html
      main.tsx
      App.tsx
      components/
        OnboardingCard.tsx
        CapturePanel.tsx
        SessionList.tsx
        ScoreEditor.tsx
        ExportPanel.tsx
        PrivacyNotice.tsx
        EmptyState.tsx
        ErrorState.tsx
    core/
      types.ts
      storage.ts
      exportMarkdown.ts
      exportJson.ts
      promptBuilder.ts
      scoring.ts
      date.ts
  docs/
    VIBEGRAPH_EXTENSION_GUIDE.md
    EXTENSION_ARCHITECTURE.md
```

---

## 필수 기능

### 1. 확장 설치 후 사이드패널 열기

- Chrome action 버튼 클릭 시 side panel이 열리도록 구현.
- 사이드패널 첫 화면에 3단계 안내 표시:
  1. AI 대화창 열기
  2. `현재 대화 캡처` 클릭
  3. 점수/태그 입력 후 리포트 프롬프트 복사 또는 내보내기

---

### 2. 지원 사이트 감지

지원 후보:

- `https://claude.ai/*`
- `https://chatgpt.com/*`
- `https://chat.openai.com/*`
- `https://gemini.google.com/*`

지원하지 않는 페이지에서는 친절한 안내 표시:

```text
현재 페이지는 아직 지원하지 않습니다.
Claude, ChatGPT, Gemini 대화창에서 사용해 주세요.
```

---

### 3. 현재 대화 캡처

- 사용자가 사이드패널의 `현재 대화 캡처` 버튼을 누르면 현재 탭의 content script가 실행/응답.
- 각 adapter는 다음 정보를 최대한 추출:
  - `source`: `claude | chatgpt | gemini | unknown`
  - `title`
  - `url`
  - `capturedAt`
  - `messages`: `role(user|assistant|system|unknown)`, `text`, `order`
- DOM 구조가 바뀌거나 메시지를 못 찾으면 앱이 죽지 않고 안내 표시.
- 긴 대화는 우선 최근 메시지 위주로라도 저장 가능하게 처리하되, 추후 확장 가능하게 구조화.
- 캡처 결과가 비어 있으면 사용자가 수동으로 제목/메모를 작성해 저장할 수 있게 할 것.

---

### 4. 세션 저장

로컬 우선 저장.

- 가능하면 IndexedDB 사용.
- 단순 설정값은 `chrome.storage.local` 사용 가능.
- 서버 저장, 외부 API 호출 금지.

데이터 스키마:

```ts
export type SessionSource = 'claude' | 'chatgpt' | 'gemini' | 'unknown';
export type MessageRole = 'user' | 'assistant' | 'system' | 'unknown';

export interface VibeMessage {
  role: MessageRole;
  text: string;
  order: number;
}

export interface VibeScores {
  oneShot: number;
  context: number;
  control: number;
  clarity: number;
}

export interface VibeSession {
  id: string;
  source: SessionSource;
  title: string;
  url: string;
  project: string;
  task: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  capturedAt: string;
  messages: VibeMessage[];
  scores?: VibeScores;
  notes?: string;
  promptSmells?: string[];
}
```

---

### 5. 점수 입력 UI

VibeGraph 기존 컨셉에 맞춰 4축 수동 점수 입력:

| 항목 | 점수 범위 | 설명 |
|---|---:|---|
| 원샷 달성률 | 0~25 | 처음 요청으로 얼마나 잘 진행됐는가 |
| 컨텍스트 유지력 | 0~25 | 중간에 맥락이 얼마나 잘 유지됐는가 |
| 주도권 제어력 | 0~25 | 사용자가 AI에게 끌려가지 않고 방향을 잡았는가 |
| 프롬프트 선명도 | 0~25 | 요청이 구체적이고 실행 가능했는가 |

요구사항:

- 합계 100점 표시.
- 점수 입력 전에는 `아직 평가 전` 상태 표시.
- 숫자 범위 오류 방지.
- 빈 값, NaN, 음수, 25 초과 입력 방지.

---

### 6. VibeGraph 리포트 프롬프트 생성

- 저장된 세션 내용을 기반으로 AI 대화창에 붙여넣을 프롬프트 생성.
- 버튼명: `리포트 프롬프트 복사`
- API 호출 없이 클립보드 복사만 수행.

프롬프트는 다음 JSON 형식 답변을 요구해야 함:

```json
{
  "summary": "...",
  "scores": {
    "oneShot": 0,
    "context": 0,
    "control": 0,
    "clarity": 0
  },
  "promptSmells": [],
  "goodExamples": [],
  "badExamples": [],
  "nextActions": []
}
```

프롬프트에는 다음 내용 포함:

- 프로젝트명
- 작업명
- 태그
- 대화 출처
- URL
- 캡처 시각
- 대화 원문 또는 요약용 원문
- 평가 기준
- JSON 출력 요구

---

### 7. Export

필수 Export:

- 선택 세션 Markdown 다운로드
- 선택 세션 JSON 다운로드
- 전체 세션 JSON 백업 다운로드

Markdown에는 다음 섹션 포함:

```markdown
# VibeGraph Session

## 기본 정보

## 점수

## 태그

## 대화 요약용 원문

## 메모

## 다음 작업
```

---

### 8. 사용자 친화 UI/UX

반드시 포함:

- 첫 실행 온보딩
- 개인정보 안내
- 지원 사이트가 아닐 때 안내
- 캡처 실패 시 원인 후보와 해결 방법 안내
- 빈 세션 목록 안내
- 성공 토스트

개인정보 안내 문구 예시:

```text
이 확장은 서버로 대화를 전송하지 않습니다.
저장은 브라우저 로컬에만 이루어집니다.
사용자가 버튼을 누른 대화만 캡처합니다.
```

성공 토스트 예시:

```text
캡처 완료
프롬프트를 복사했어요
Markdown 파일을 만들었어요
JSON 백업을 만들었어요
```

버튼 라벨은 개발자스럽게 어렵지 않게 작성:

| 피할 표현 | 권장 표현 |
|---|---|
| Parse DOM | 현재 대화 캡처 |
| Generate Payload | 리포트 프롬프트 복사 |
| Serialize Session | JSON 백업 |
| Export MD | Markdown 저장 |
| Unsupported Host | 아직 지원하지 않는 페이지예요 |

---

## 권한 원칙

권한은 최소화:

```json
{
  "permissions": [
    "sidePanel",
    "storage",
    "activeTab",
    "scripting"
  ],
  "host_permissions": [
    "https://claude.ai/*",
    "https://chatgpt.com/*",
    "https://chat.openai.com/*",
    "https://gemini.google.com/*"
  ]
}
```

---

## 권장 package scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "typecheck": "tsc -b",
    "preview": "vite preview"
  }
}
```

---

## 문서 작성 요구사항

### `extension/docs/VIBEGRAPH_EXTENSION_GUIDE.md`

포함 내용:

- 이 확장이 무엇인지
- local 방식과 web 방식 차이
- 설치 방법
- `chrome://extensions` 개발자 모드에서 unpacked 로드하는 방법
- 기본 사용 흐름
- 데이터가 어디에 저장되는지
- 지원 사이트
- 제한사항
- 문제 해결
- 향후 Pro 기능 후보

### `extension/docs/EXTENSION_ARCHITECTURE.md`

포함 내용:

- 전체 구조 ASCII 다이어그램
- content script / service worker / side panel / storage 역할
- 데이터 흐름
- adapter 구조
- 보안/개인정보 원칙
- 향후 Native Messaging 또는 기존 CLI 연동 계획

---

## 빌드/검증

- `extension` 폴더에서 `npm install` 후 `npm run build` 가능해야 함.
- `npm run typecheck` 제공.
- 빌드 산출물을 Chrome 확장 개발자 모드에서 로드 가능해야 함.
- README 또는 docs에 로드 경로 명시.
- TypeScript 오류 없이 통과.
- 기존 `vibegraph` Python CLI 관련 파일은 깨지지 않아야 함.

---

## 완료 기준

1. Chrome에서 개발자 모드로 `extension/dist` 또는 빌드 산출물 로드 가능.
2. Claude.ai / ChatGPT / Gemini 중 최소 1개 사이트에서 현재 대화 캡처 성공.
3. 지원하지 않는 페이지에서 친절한 안내 표시.
4. 세션 저장/목록/선택/수정 가능.
5. 4축 점수 입력 가능.
6. 리포트 프롬프트 복사 가능.
7. Markdown/JSON Export 가능.
8. `extension/docs/VIBEGRAPH_EXTENSION_GUIDE.md`와 `extension/docs/EXTENSION_ARCHITECTURE.md` 작성 완료.
9. 기존 CLI 기능 손상 없음.

---

## 테스트 체크리스트

```text
[ ] npm install 성공
[ ] npm run typecheck 성공
[ ] npm run build 성공
[ ] chrome://extensions에서 unpacked 로드 성공
[ ] 지원하지 않는 페이지에서 안내 표시
[ ] Claude/ChatGPT/Gemini 중 최소 1개에서 캡처 성공
[ ] 캡처 실패 시 앱이 죽지 않음
[ ] 세션 저장/수정/삭제 또는 목록 관리 가능
[ ] 4축 점수 입력 가능
[ ] 총점 계산 정상
[ ] 리포트 프롬프트 복사 정상
[ ] Markdown 다운로드 정상
[ ] JSON 다운로드 정상
[ ] 전체 백업 다운로드 정상
[ ] 기존 Python CLI 실행/패키지 구조 손상 없음
```

---

## 진행 방식 제안

1. `feature/chrome-extension-mvp` 브랜치 생성.
2. 기존 CLI 테스트 가능 여부 확인.
3. `extension/` 독립 프로젝트 생성.
4. Manifest V3 + Side Panel 기본 UI 구현.
5. 저장소/타입/Export 코어 구현.
6. ChatGPT 또는 Claude 중 하나부터 adapter 구현.
7. 나머지 adapter는 best-effort로 추가.
8. 문서 작성.
9. 빌드/타입체크 결과 정리.

---

## 주의

- DOM selector는 깨질 수 있으므로 adapter별로 여러 후보 selector를 두고 실패해도 앱 전체가 죽지 않게 처리.
- 캡처 결과가 비어 있으면 사용자가 수동으로 제목/메모를 작성해 저장할 수 있게 할 것.
- 확장 설명과 UI에서 과장 금지.
- 표현은 “자동으로 실력을 올려준다”가 아니라 “작업 대화를 정리하고 회고를 도와준다”로 작성.
