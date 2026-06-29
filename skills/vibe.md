---
description: VibeGraph 바이브코딩 채점 + Domain Learning Card 관리. start/report/end/list/dashboard/growth/coach/learn 지원.
argument-hint: start <project> <task> | report | end | list | dashboard | growth | coach | learn <list|add|show|next|done|archive|reopen|add-reference|export|report|stats>
allowed-tools: [PowerShell, Read, Write]
---

사용자가 입력한 인수: $ARGUMENTS

아래 규칙에 따라 처리한다.

---

## 명령어 분기

`$ARGUMENTS`의 첫 번째 단어를 subcommand로 처리한다.

**중요: vibe는 Windows 명령이므로 반드시 PowerShell 도구로 실행한다.**

### start / end / list / stats / dashboard / growth / coach / learn

PowerShell 도구로 실행 후 출력을 보여준다:

```powershell
$env:PYTHONUTF8 = "1"; vibe $ARGUMENTS
```

`learn` 명령 접근 경로:
- Claude Code 창: `/vibe learn list`
- 터미널: `vibe learn list`
- 필터 조회: `vibe learn list --all --domain "<도메인>" --type "<타입>" --severity 4 --search "<검색어>"`
- 제한 조회: `vibe learn list --limit 5`
- 정렬 조회: `vibe learn list --sort severity`
- 복습 대상 조회: `vibe learn list --due`
- JSON 목록 조회: `vibe learn list --all --json`
- 수동 카드 생성: `vibe learn add --domain "<도메인>" --type "<타입>" --title "<제목>"`
- 카드 보기: `vibe learn show <id>`
- JSON 카드 보기: `vibe learn show <id> --json`
- 다음 카드 보기: `vibe learn next`
- 다음 카드 JSON: `vibe learn next --json`
- 완료 처리: `vibe learn done <id>`
- 보관 처리: `vibe learn archive <id>`
- 복습일 설정: `vibe learn schedule <id> --date 2026-07-01`
- 다시 열기: `vibe learn reopen <id>`
- 참고 링크 추가: `vibe learn add-reference <id> --title "<제목>" --url "<URL>"`
- Markdown 생성: `vibe learn export`
- 짧은 집계: `vibe learn stats`
- JSON 집계: `vibe learn stats --json`

### report — 현재 대화 자동 채점 + 리포트 생성

**이 대화(현재 컨텍스트의 전체 내용)를 Claude가 직접 채점하고 리포트를 생성한다.**
소급 채점 지원: 이미 끝난 대화에서 `start` 직후 `report`를 실행해도 동작한다.

**Step 1 — 세션 확인:**

PowerShell 도구로 실행:
```powershell
$env:PYTHONUTF8 = "1"; python -c "import os,json; from pathlib import Path; r=Path(os.environ.get('VIBE_HOME') or os.environ.get('VIBEFIX_HOME') or str(Path.home()/'.vibegraph')); f=r/'.current_session.json'; print(f.read_text(encoding='utf-8') if f.exists() else 'NO_SESSION')"
```

출력이 `NO_SESSION`이면 → "세션 없음. `/vibe start <project> <task>` 를 먼저 실행하세요." 안내 후 종료.

**Step 2 — 현재 대화 채점 (Claude 직접 수행):**

이 대화의 전체 내용(현재 컨텍스트에 있는 사용자↔Claude 모든 교환)을 아래 4축으로 채점한다.

채점 기준(각 25점):
- `one_shot` — 요구사항·제약(환경/버전/파일구조)을 한 번에 줘서 불필요한 수정 턴을 줄였는가
- `context_drift` — 초기 목표 유지, 컨텍스트 오염·무의미한 왕복 없었는가
- `ai_control` — 땜질·우회 제안에 안 휩쓸리고 사람이 방향을 주도했는가
- `prompt_clarity` — 모호한 표현 없이 에러로그·소스 스니펫 등 명확한 컨텍스트를 줬는가

채점 태도(보수적):
- 기본 출발점 각 13점. 명백한 근거가 있을 때만 위로 올린다.
- 의심스러우면 낮은 쪽. 사소한 마찰도 반드시 감점.
- 보통 대화 total 정상 범위: 60~75(B~C). 80(A) 이상은 확실한 근거 필요.
- 등급: S(92+) / A(82-91) / B(70-81) / C(≤69)

`prompt_smells.type`은 다음 중 하나:
`"Missing Context"`, `"Vague Instruction"`, `"Scope Creep"`, `"Patch Acceptance"`,
`"Repeat Question"`, `"Over-specification"`, `"Environment Mismatch"`, `"Tool Misuse"`

**Domain Learning 추가 분석:**

이번 대화에서 드러난 개발/DB/인프라/업무도메인 지식 공백을 찾아라.
단순 오타나 일회성 실수는 제외하고, 다음 작업의 정확도/속도/장애대응에 영향을 주는 것만 추출한다.
프롬프트 문제(`prompt_gap`)와 도메인 지식 문제(`concept_gap`, `error_pattern`, `tool_gap`, `environment_gap`, `domain_gap`, `decision_gap`)를 구분한다.
각 Learning Signal은 하루 5~10분 안에 복습 가능한 작은 카드가 되어야 한다.
확실한 공식문서/대표 자료가 있을 때만 `references`에 넣고, 확실하지 않으면 빈 배열로 둔다. URL을 지어내지 마라.

**Step 3 — result.json 기록:**

Step 1에서 읽은 session JSON의 `task_dir` 값 경로에 `result.json`을 Write 도구로 저장.
아래 구조를 실제 채점 결과로 채워서 저장:

```json
{
  "scores": {"one_shot": 0, "context_drift": 0, "ai_control": 0, "prompt_clarity": 0, "total": 0},
  "grade": "B",
  "grade_reason": "1~2문장 근거",
  "turn_count": 0,
  "est_tokens": 0,
  "turn_purity": [50, 60, 55],
  "prompt_smells": [
    {"turn_desc": "발생 시점", "description": "구체적 문제", "type": "Vague Instruction", "wasted_turns": 1}
  ],
  "good_bad_examples": [
    {"context": "상황", "bad": "안 좋은 프롬프트", "good": "개선된 프롬프트", "expected_effect": "기대 효과"}
  ],
  "skill_recommendations": [
    {"situation": "작업 상황", "used_approach": "사용한 방식", "better_skill": "더 나은 도구/방법", "reason": "이유"}
  ],
  "domain_learning": {
    "session_learning_summary": "이번 세션에서 드러난 도메인 지식 공백 요약",
    "learning_signals": [
      {
        "id": "LC-YYYYMMDD-topic",
        "domain": "Java|Spring|MyBatis|Oracle|CUBRID|SQL|Linux|Docker|Tomcat|JEUS|JBoss|Jenkins|Network|React|TypeScript|AI-Collaboration|Business-Domain|Etc",
        "type": "concept_gap|error_pattern|tool_gap|environment_gap|domain_gap|prompt_gap|decision_gap",
        "title": "5~10분 복습 카드 제목",
        "evidence": "대화에서 이 공백이 드러난 구체적 근거",
        "severity": 1,
        "recurrence": 1,
        "confidence": "low|medium|high",
        "micro_summary": "핵심 개념 1줄 요약",
        "micro_goal": "다음 작업 전에 5분 안에 설명할 수 있어야 할 목표",
        "self_checkpoints": ["다음 작업 시 확인할 질문"],
        "references": []
      }
    ]
  },
  "summary": "전체 요약 2~3문장",
  "top_improvement": "가장 중요한 개선점 1가지"
}
```

**Step 4 — 리포트 생성:**

PowerShell 도구로 실행:
```powershell
$env:PYTHONUTF8 = "1"; vibe end
```

완료 후 report.html 경로를 안내한다.
Domain Learning Card가 저장되었으면 접근 경로도 함께 안내한다:
- 터미널 > `vibe learn list`
- Claude Code 창 > `/vibe learn list`

---

## VibeGraph CLI 미설치 시

```powershell
pip install git+https://github.com/seamoon23/vibegraph.git
vibe install-skill
```

설치 후 VS Code를 **완전히 재시작**해야 `/vibe` 명령이 인식됩니다.
