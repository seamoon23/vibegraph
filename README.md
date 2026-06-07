# 🎯 VibeGraph

> 바이브코딩(AI 페어 프로그래밍) 대화의 **순도**를 사후 채점하고, 성장 흐름을 추적하는 CLI

작업이 끝날 때마다 "이번 대화에서 내가 AI를 얼마나 잘 이끌었나"를 4개 항목(각 25점)으로 채점하고,
HTML 리포트·조회 페이지·누적 성장 리포트·맞춤 코칭까지 만들어 줍니다.

**별도 API 키·추가 결제가 필요 없습니다.** 채점은 평소 쓰던 Claude Code 창에서 이뤄집니다(Pro/Max 구독으로 커버).

---

## ✨ 특징

- **4축 채점** — 원샷 달성률 · 컨텍스트 유지력 · 주도권 제어력 · 프롬프트 선명도
- **API-free** — 대화 맥락을 가진 Claude 창에서 직접 채점 (외부 API 호출 없음)
- **개별 리포트** — 점수·레이더 차트·Prompt Smell·Good/Bad 예시·대체 스킬 추천
- **전체 조회 페이지** (`index.html`) — 검색·프로젝트·기간 필터, 정렬, 필터 결과 KPI
- **성장 리포트** (`growth.html`) — 점수 추세, 가장 약한 항목, 반복 스멜, 프로젝트별 평균
- **누적 코칭** (`vibe coach`) — 계산으로 추출한 신호를 근거로 한 맞춤 코칭 (억지 분석 방지)

## 📦 요구 사항

- Windows 10/11
- Python 3.8+ ([python.org](https://www.python.org/downloads/) — 설치 시 **"Add Python to PATH"** 체크)

## 🚀 설치

1. 이 저장소를 내려받아 원하는 위치에 둡니다. (한글·공백 없는 경로 권장)
   ```
   git clone https://github.com/<your-id>/vibegraph.git
   ```
2. 폴더 안의 **`install.bat`** 을 더블클릭합니다. (Python 확인 + `vibe` 명령 PATH 등록)
3. **새 터미널**(또는 VS Code 완전 재시작) 후 사용합니다.

> 💡 설치 후 `vibe` 가 "인식되지 않습니다"라고 나오면, 그 터미널이 옛 환경변수를 들고 있는 것입니다.
> **VS Code를 완전히 종료 후 재실행**하거나 **새 PowerShell 창**을 여세요. (install.bat 재실행 불필요)

## 🧭 기본 사용법

```bash
vibe start <프로젝트> <작업명>   # 작업 시작 (작업명에 공백 가능)
#  … Claude Code로 평소처럼 작업 …
vibe prompt                      # 채점 프롬프트 복사 + result.json 열기
#  → 작업하던 Claude 창에 붙여넣기 → 나온 JSON을 result.json 에 저장
vibe end                         # 리포트(report.html) 생성 + 조회/성장 페이지 갱신
```

| 명령 | 설명 |
|---|---|
| `vibe start <project> <task>` | 새 작업 세션 시작 |
| `vibe prompt` | 채점 프롬프트 복사 + `result.json` 열기 |
| `vibe end` | `result.json` 으로 리포트 생성 (+ 조회/성장 페이지 자동 갱신) |
| `vibe list [project]` | 작업 목록 |
| `vibe stats [--weeks N]` | 기간별 통계 |
| `vibe dashboard` | 전체 작업 조회 페이지 (= `view`, `index`) |
| `vibe growth` | 성장 리포트 — 기본 **최근 2주** (`--all` 전체 · `--weeks N` · `--project <이름>`) |
| `vibe coach` | 누적 신호 기반 코칭 프롬프트 복사 |

> ⏱ **성장 리포트 기본 기간이 "최근 2주"인 이유**: 전체를 기본으로 하면 작업이 쌓일수록 집계가 느려지고 추세 차트가 복잡해집니다. 그래서 `vibe end` 자동 생성과 `vibe growth` 기본값 모두 최근 2주만 봅니다. 전체 흐름은 `vibe growth --all` 로 확인하세요.

자세한 흐름은 **`가이드.html`** (더블클릭) 또는 **`사용법.txt`** 를 참고하세요.

## 📁 데이터 저장 위치

채점 데이터는 **코드와 분리**되어 사용자 폴더에 쌓입니다.

```
~/.vibegraph/                     (= %USERPROFILE%\.vibegraph)
 ├ index.html        전체 작업 조회 페이지
 ├ growth.html       누적 성장 리포트
 └ <프로젝트>/<날짜_작업명>/
     ├ result.json   Claude가 출력한 채점 결과
     ├ data.json     최종 점수 데이터(통계 연동)
     └ report.html   개별 리포트
```

- 저장 위치를 바꾸려면 환경변수 **`VIBE_HOME`** 에 원하는 경로를 지정하세요.
- 구버전(코드 폴더에 데이터가 쌓이던 방식)에서 올라오면, 첫 실행 때 데이터를 사용자 폴더로 **자동 이전**합니다.

## 🔒 왜 API 키가 필요 없나

채점을 *작업하던 Claude Code 창*에서 하기 때문입니다. 그 창은 이미 대화 맥락을 갖고 있어,
프롬프트만 붙여넣으면 스스로 채점 JSON을 출력합니다. 이 CLI는 폴더 정리·HTML 생성·통계만 담당합니다.

## 📄 라이선스

MIT (원하는 라이선스로 교체하세요)
