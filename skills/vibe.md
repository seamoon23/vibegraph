---
name: vibe
description: VibeGraph 바이브코딩 채점. /vibe start <proj> <task>로 세션 시작, /vibe report로 현재 대화를 자동 채점해 HTML 리포트 완결. 소급 채점(이미 끝난 대화에서도 동작) 지원.
---

# VibeGraph Skill

사용자가 `/vibe <subcommand> [args]`를 입력하면 아래 규칙대로 처리한다.

---

## 일반 명령어 — CLI 위임

아래 명령어는 Bash 도구로 그대로 실행하고 출력을 보여준다:

- `/vibe start <project> <task>` → `vibe start <project> <task>`
- `/vibe end` → `vibe end`
- `/vibe list [project]` → `vibe list [project]`
- `/vibe stats [--weeks N]` → `vibe stats [--weeks N]`
- `/vibe dashboard` → `vibe dashboard`
- `/vibe growth [--all] [--weeks N] [--project X]` → `vibe growth [해당 옵션]`
- `/vibe coach` → `vibe coach`

---

## /vibe report — 현재 대화 자동 채점 + 리포트 생성

**핵심 명령어. 현재 컨텍스트의 대화 전체를 Claude가 직접 채점한다.**
소급 채점 지원: 이미 끝난 대화에서 `/vibe start` 직후 `/vibe report`를 실행해도 동작한다.

### Step 1 — 세션 확인

```bash
python -c "
import os
from pathlib import Path
root = Path(os.environ.get('VIBE_HOME') or os.environ.get('VIBEFIX_HOME') or str(Path.home() / '.vibegraph'))
sf = Path(root) / '.current_session.json'
print(sf.read_text(encoding='utf-8') if sf.exists() else 'NO_SESSION')
"
```

출력이 `NO_SESSION`이면 → "세션 없음. `/vibe start <project> <task>` 를 먼저 실행하세요." 안내 후 종료.

### Step 2 — 현재 대화 채점 (Claude 직접 수행)

이 대화의 전체 내용(현재 컨텍스트에 있는 사용자↔Claude 모든 교환)을 아래 4축으로 채점한다.

**채점 기준 — 각 25점:**
1. `one_shot` — 요구사항·제약(환경/버전/파일구조)을 한 번에 줘서 불필요한 수정 턴을 줄였는가
2. `context_drift` — 초기 목표 유지, 컨텍스트 오염·무의미한 왕복 없었는가
3. `ai_control` — 땜질·우회 제안에 안 휩쓸리고 사람이 방향을 주도했는가
4. `prompt_clarity` — 모호한 표현 없이 에러로그·소스 스니펫 등 명확한 컨텍스트를 줬는가

**채점 태도 — 보수적:**
- 기본 출발점 각 13점. 명백한 근거가 있을 때만 위로 올린다.
- 의심스러우면 낮은 쪽. 사소한 마찰(되묻기 1번, 모호한 표현 1번)도 반드시 감점.
- 보통 대화의 total 정상 범위: 60~75 (B~C). 80(A) 이상은 확실한 근거 필요.
- 등급: S(92+) / A(82-91) / B(70-81) / C(≤69)

`prompt_smells.type`은 다음 중 하나:
`"Missing Context"`, `"Vague Instruction"`, `"Scope Creep"`, `"Patch Acceptance"`,
`"Repeat Question"`, `"Over-specification"`, `"Environment Mismatch"`, `"Tool Misuse"`

### Step 3 — result.json 기록

Step 1에서 읽은 session JSON의 `task_dir` 값을 경로로, `<task_dir>/result.json` 파일을
Write 도구로 저장한다. 아래 구조를 실제 채점 결과로 채워서 저장:

```json
{
  "scores": {"one_shot": 0, "context_drift": 0, "ai_control": 0, "prompt_clarity": 0, "total": 0},
  "grade": "B",
  "grade_reason": "1~2문장 근거",
  "turn_count": 0,
  "est_tokens": 0,
  "turn_purity": [50, 60, 55],
  "prompt_smells": [
    {"turn_desc": "발생 시점 요약", "description": "구체적 문제", "type": "Vague Instruction", "wasted_turns": 1}
  ],
  "good_bad_examples": [
    {"context": "상황", "bad": "안 좋은 프롬프트 예시", "good": "개선된 프롬프트 예시", "expected_effect": "기대 효과"}
  ],
  "skill_recommendations": [
    {"situation": "작업 상황", "used_approach": "사용한 방식", "better_skill": "더 나은 도구/방법", "reason": "이유"}
  ],
  "summary": "전체 요약 2~3문장",
  "top_improvement": "가장 중요한 개선점 1가지"
}
```

### Step 4 — 리포트 생성

```bash
vibe end
```

완료 후 report.html 경로를 사용자에게 안내한다.

---

## VibeGraph CLI 미설치 시

```bash
pip install git+https://github.com/seamoon23/vibegraph.git
vibe install-skill
```

설치 후 VS Code를 **완전히 재시작**해야 `/vibe` 명령이 인식됩니다.
터미널(외부) vs Claude Code 창 구분: `vibe start/end/list` 등 파일 조작 명령은 터미널,
`/vibe report`의 채점은 Claude Code 창 안에서 이뤄집니다.
