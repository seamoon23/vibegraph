# VibeGraph Extension Time Flow Report Plan

## 결론

시간대 흐름 리포트는 단계적으로 가능하다.

- 세션 단위 흐름: 현재 `capturedAt`, `createdAt`, `updatedAt`, `scores`가 있어 바로 가능하다.
- 대화 턴 단위 흐름: 현재 `VibeMessage`에 턴별 timestamp가 없어 정확한 시간 그래프는 아직 어렵다.
- CLI 수준의 성장 리포트와 연결: 확장기능에서 세션 단위 추세를 먼저 만들고, 나중에 CLI import 또는 Native Messaging이 붙으면 통합할 수 있다.

## 1차 범위

확장기능 안에서 무료로 처리한다.

- 날짜순 점수 추이
- 최근 N개 세션 평균
- 가장 약한 축 변화
- 프로젝트별 평균
- 반복 Prompt Smell 변화
- 전반부와 후반부 비교

## 필요한 데이터

이미 있음:

- `VibeSession.capturedAt`
- `VibeSession.updatedAt`
- `VibeSession.project`
- `VibeSession.task`
- `VibeSession.scores`
- `VibeSession.promptSmells`

추가하면 좋은 데이터:

- `VibeMessage.timestamp`
- 평가 방식: `manual | localDraft | ai`
- 리포트 생성 시각
- 저장 확정 시각

## 후속 구현안

1. `core/timelineReport.ts` 추가
2. 전체 흐름 리포트 아래에 `시간 흐름` 탭 추가
3. 최근 5개/10개/전체 토글 제공
4. 텍스트 막대 그래프부터 적용
5. 나중에 전체 화면 리포트 페이지에서 Chart.js 또는 SVG 그래프 적용

## 주의점

현재 Chrome 확장기능은 로컬 우선 MVP라 외부 API 없이 동작한다. 따라서 시간대 리포트도 1차는 결정론적 분석으로 만들고, AI 해석은 전체 리포트 프롬프트 복사 흐름에 맡긴다.
