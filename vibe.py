#!/usr/bin/env python3
"""
VibeGraph - 바이브코딩 대화 순도 분석 CLI  (API 키 불필요)
Usage:
  vibe start <project> <task>   - 새 작업 세션 시작
  vibe prompt                   - 채점 프롬프트 복사 + result.json 열기
  vibe end [--file <path>]      - result.json 으로 리포트 생성
  vibe list [<project>]         - 세션 목록 조회
  vibe stats [--weeks <n>]      - 기간별 통계 요약
  vibe dashboard                - 전체 작업 조회 페이지(index.html) 생성/열기
  vibe growth                   - 누적 성장 리포트(growth.html) 생성/열기
  vibe coach                    - 누적 신호 기반 코칭 프롬프트 복사 (Claude창에서 코칭)

채점은 '작업하던 Claude Code 창'에서 이뤄진다(Pro 구독으로 커버).
이 CLI는 폴더 정리·HTML 생성·통계만 담당하며 외부 API를 호출하지 않는다.
"""

import os
import sys
import json
import argparse
import datetime
from pathlib import Path

# 코드가 있는 폴더(설치 위치). 데이터와 분리하기 위해 따로 둔다.
SCRIPT_DIR = Path(__file__).resolve().parent


def _looks_like_project_dir(p: Path) -> bool:
    """하위에 'YYYYMMDD...' 작업 폴더를 가진 디렉터리면 사용자 데이터로 본다."""
    if not p.is_dir() or p.name.startswith("."):
        return False
    try:
        for c in p.iterdir():
            if c.is_dir() and len(c.name) >= 8 and c.name[:8].isdigit():
                return True
    except OSError:
        return False
    return False


def _resolve_root() -> Path:
    """데이터 루트 결정.
      1) VIBE_HOME(구: VIBEFIX_HOME) 환경변수가 있으면 그 경로.
      2) 없으면 ~/.vibegraph (코드 저장소와 분리 — GitHub 공개·clean 안전).
    구버전 데이터(.vibepurity 또는 코드 폴더)는 자동으로 이어받는다."""
    env = os.environ.get("VIBE_HOME") or os.environ.get("VIBEFIX_HOME")
    if env:
        return Path(env)

    data = Path.home() / ".vibegraph"

    # (1) 이전 이름(.vibepurity)의 데이터를 통째로 이어받기
    old = Path.home() / ".vibepurity"
    if old.exists() and not data.exists():
        try:
            import shutil
            shutil.move(str(old), str(data))
            print(f"ℹ  데이터 폴더 이름을 갱신했습니다: {old.name} → {data.name}")
        except Exception:
            pass

    # (2) 더 구버전: 코드 폴더에 쌓인 데이터를 사용자 폴더로 1회 이전
    marker = SCRIPT_DIR / ".migrated_to_userdir"
    if not marker.exists() and SCRIPT_DIR.exists():
        try:
            legacy = [p for p in SCRIPT_DIR.iterdir() if _looks_like_project_dir(p)]
        except OSError:
            legacy = []
        if legacy:
            import shutil
            data.mkdir(parents=True, exist_ok=True)
            moved = 0
            for p in legacy:
                dest = data / p.name
                if not dest.exists():
                    try:
                        shutil.move(str(p), str(dest))
                        moved += 1
                    except Exception:
                        pass
            for fn in (".current_session.json", "index.html", "growth.html"):
                src = SCRIPT_DIR / fn
                if src.exists() and not (data / fn).exists():
                    try:
                        shutil.move(str(src), str(data / fn))
                    except Exception:
                        pass
            try:
                marker.write_text(f"데이터를 {data} 로 이전했습니다.\n", encoding="utf-8")
            except Exception:
                pass
            if moved:
                print(f"ℹ  기존 데이터를 사용자 폴더로 이전했습니다 → {data}")
                print(f"   (코드 폴더와 분리되어 GitHub 공개·업데이트가 안전해집니다)")
    return data


# 데이터 루트(채점 결과·통계·조회페이지가 쌓이는 곳)
ROOT = _resolve_root()
SESSION_FILE = ROOT / ".current_session.json"


def _open_path(path) -> None:
    """OS 기본 앱으로 파일을 연다 (실패해도 조용히 무시 — 크로스플랫폼 안전)."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            import subprocess
            subprocess.Popen(["open", str(path)])
        else:
            import subprocess
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass


# 작업하던 Claude Code 창에 그대로 붙여넣으면, Claude가 이번 대화를 스스로 채점하고
# 도구/스킬 추천까지 담은 result.json 을 출력해 준다. (API 불필요 — Pro 구독으로 커버)
ANALYSIS_PROMPT = """지금부터 너는 시니어 프롬프트 엔지니어이자 AI 협업 코치다.
방금까지 "우리가 이번 작업에서 나눈 대화 전체"를 사후 평가해줘.
나는 바이브코딩 습관을 개선하려는 개발자다.

[작업 환경 맥락]
Java 레거시(1.6~1.8) + Spring + MyBatis + Oracle/MariaDB/Cubrid + Tomcat/JEUS/JBoss 의
유지보수·기능개발(건바이건) 작업이다.

[채점 기준 — 각 25점]
1. one_shot        요구사항·제약(환경/버전/파일구조)을 한 번에 줘서 불필요한 수정 턴을 줄였는가
2. context_drift   초기 목표를 유지하고 컨텍스트 오염·무의미한 왕복이 없었는가
3. ai_control      땜질·우회 제안에 휩쓸리지 않고 사람이 아키텍처/방향을 주도했는가
4. prompt_clarity  모호한 표현을 배제하고 에러로그·소스 스니펫 등 명확한 컨텍스트를 줬는가

[채점 태도 — 매우 보수적으로]
- 너는 점수에 인색한 깐깐한 평가자다. "잘했다"보다 "어디가 부족했나"를 먼저 본다.
- 기본 출발점은 만점이 아니라 중간(각 항목 13점)이다. 명백한 근거가 있을 때만 위로 올린다.
- 의심스러우면 무조건 낮은 쪽으로 준다. 좋게 봐주지 마라.
- 사소한 마찰(되묻기 1번, 모호한 표현 1번, AI 제안에 그냥 수긍 1번)도 반드시 감점한다.
- 각 항목 점수대 기준(엄격 적용):
    23~25 : 흠잡을 데 거의 없음. 이런 경우는 드물다. 확실한 근거 없으면 주지 마라.
    18~22 : 잘했지만 1~2개 분명한 개선점 존재.
    13~17 : 평범. 마찰/되묻기/모호함이 눈에 띔. (대부분의 보통 대화가 여기)
    7~12  : 비효율 반복, 컨텍스트 부족, AI에 끌려간 정황.
    0~6   : 목표 흐트러짐·땜질 수용·반복 실패가 두드러짐.
- 전체 total 이 80(A) 이상은 "정말 모범적인 대화"에만 허용해라. 보통의 무난한 대화는 60~75(B~C)가 정상이다.

[반드시 포함 — 도구/스킬 추천]
대화에서 내가 비효율적으로 한 지점을 보고 "그 작업엔 이 방법/스킬/도구가 더 나았다"를 구체적으로 제안해.
예) 직접 grep 반복 → Explore 에이전트 위임 / 거대 코드 통째 붙여넣기 → 파일 경로 참조 /
   다단계 작업 → plan 먼저 / 반복 수정 유발 → 처음에 제약 한 번에 명시 / 단순 조사 → 가벼운 도구로 위임.

[출력 규칙]
- 아래 JSON "한 덩어리만" 출력한다. 인사말·해설 없이. (```json 펜스는 써도 된다)
- 점수는 정수, total 은 4개 합.
- turn_count 는 이번 대화의 사용자↔AI 왕복 횟수(정수). 네가 정확히 셀 수 있다.
- est_tokens 는 이번 대화에서 소비된 총 토큰의 "대략 추정치"(정수). 정확값 아니어도 된다.
- turn_purity 는 대화를 최대 10구간으로 나눈 각 구간 순도(0~100) 배열.
- grade: S(92+) A(82-91) B(70-81) C(69 이하)  ※ 컷이 높다. 후하게 매기지 마라.
- prompt_smells.type 은 다음 중 하나:
  "Missing Context","Vague Instruction","Scope Creep","Patch Acceptance",
  "Repeat Question","Over-specification","Environment Mismatch","Tool Misuse"

{
  "scores": {"one_shot":0,"context_drift":0,"ai_control":0,"prompt_clarity":0,"total":0},
  "grade": "S|A|B|C",
  "grade_reason": "1~2문장",
  "turn_count": 0,
  "est_tokens": 0,
  "turn_purity": [0],
  "prompt_smells": [
    {"turn_desc":"발생 시점 요약","description":"구체적 문제","type":"분류명","wasted_turns":0}
  ],
  "good_bad_examples": [
    {"context":"상황","bad":"안 좋았던 프롬프트(실제/유사)","good":"리팩토링된 베스트 프롬프트","expected_effect":"기대 효과"}
  ],
  "skill_recommendations": [
    {"situation":"이런 작업을 할 때","used_approach":"지금은 이렇게 처리했는데","better_skill":"이 스킬/도구/방법이 더 적합","reason":"토큰효율·정확도 등 이유"}
  ],
  "summary": "전체 요약 2~3문장",
  "top_improvement": "가장 중요한 개선점 1가지"
}
"""


# ── vibe start ─────────────────────────────────────────────────────────────────

def cmd_start(args):
    project = args.project.strip()
    task = (" ".join(args.task) if isinstance(args.task, list) else args.task).strip()

    # 직전 작업을 vibe end 로 마무리하지 않은 경우: 확인 질문(y/n)
    if SESSION_FILE.exists():
        try:
            prev = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            prev_label = f"[{prev.get('project','')}] {prev.get('task','')}"
        except Exception:
            prev = None
            prev_label = "(이전 작업)"
        print(f"\n⚠  이전 작업 {prev_label} 이(가) vibe end 로 마무리되지 않았습니다.")
        print(f"   지금 새 작업을 시작하면 이전 작업은 채점되지 않은 채 남습니다.")
        print(f"   (이전 작업을 채점하려면 먼저  vibe end  를 실행하세요.)")
        try:
            ans = input("\n   이전 작업을 그대로 두고 새 작업을 시작할까요? [y/N] ").strip().lower()
        except EOFError:
            ans = ""
        if ans not in ("y", "yes"):
            print("   ⏹  새 작업을 시작하지 않았습니다. (먼저 vibe end 후 다시 시도하세요)")
            return

    started_at = datetime.datetime.now()
    date_str = started_at.strftime("%Y%m%d")
    time_str = started_at.strftime("%H%M")
    # 작업명에서 파일시스템 금지 문자 제거
    safe_task = "".join(c for c in task if c not in r'\/:*?"<>|').strip() or "untitled"

    # 같은 날 같은 이름이 이미 있으면 고지 (시간 접미사로 충돌 자체는 회피)
    proj_dir = ROOT / project
    if proj_dir.exists():
        dup = [d.name for d in proj_dir.iterdir()
               if d.is_dir() and d.name[:8] == date_str and d.name.endswith(f"_{safe_task}")]
        if dup:
            print(f"\nℹ  오늘 같은 이름의 작업이 이미 있습니다: {dup[0]}")
            print(f"   구분을 위해 다음엔 다른 작업명을 권장합니다. (이번엔 시간으로 자동 구분됨)")

    # 폴더명: YYYYMMDD_HHMM_작업명  (앞 8자리 날짜는 그대로라 list/stats 파싱 호환)
    folder_name = f"{date_str}_{time_str}_{safe_task}"
    task_dir = proj_dir / folder_name
    # 같은 분(分)에 다시 시작해 이름이 겹치면 _2, _3... 접미사로 충돌 회피
    if task_dir.exists():
        n = 2
        while (proj_dir / f"{folder_name}_{n}").exists():
            n += 1
        folder_name = f"{folder_name}_{n}"
        task_dir = proj_dir / folder_name
    task_dir.mkdir(parents=True, exist_ok=True)

    session = {
        "project": project,
        "task": task,
        "started_at": started_at.isoformat(),
        "task_dir": str(task_dir),
    }
    SESSION_FILE.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅  작업 시작: [{project}] {task}")
    print(f"📁  폴더  : {task_dir}")
    print(f"\n  다음 순서로 진행하세요:")
    print(f"   1) Claude Code로 평소처럼 작업")
    print(f"   2) 작업이 끝나면 같은 창에서  vibe prompt  실행")
    print(f"      → 채점 프롬프트가 클립보드에 복사되고 result.json 이 열립니다")
    print(f"   3) 그 프롬프트를 '작업하던 Claude 창'에 붙여넣기")
    print(f"      → Claude가 이번 대화를 채점한 JSON을 출력합니다")
    print(f"   4) 그 JSON을 result.json 에 붙여넣고 저장")
    print(f"   5) vibe end  → report.html 생성")


# ── vibe prompt ────────────────────────────────────────────────────────────────

def _copy_to_clipboard(text: str) -> bool:
    """Windows 클립보드에 복사. 성공하면 True."""
    try:
        import subprocess
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
            input=text, text=True, encoding="utf-8", timeout=10,
        )
        return True
    except Exception:
        return False


def cmd_prompt(args):
    print(ANALYSIS_PROMPT)
    print("\n" + "─" * 55)
    if _copy_to_clipboard(ANALYSIS_PROMPT):
        print("📋  채점 프롬프트가 클립보드에 복사되었습니다.")
        print("    → '작업하던 Claude 창'에 붙여넣기(Ctrl+V) 하세요.")
    else:
        print("    (클립보드 복사 실패 - 위 내용을 직접 복사하세요)")

    # result.json 준비 후 메모장으로 열어 붙여넣기 안내
    if SESSION_FILE.exists():
        session = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
        result_path = Path(session["task_dir"]) / "result.json"
        if not result_path.exists():
            result_path.write_text(
                "여기에 Claude가 출력한 JSON 결과를 붙여넣고 저장한 뒤 vibe end 를 실행하세요.\n",
                encoding="utf-8",
            )
        print(f"    → Claude가 출력한 JSON을 여기에 저장:  {result_path}")
        _open_path(result_path)
    print("    → 저장 후  vibe end  실행")


# ── vibe end ───────────────────────────────────────────────────────────────────

def cmd_end(args):
    if not SESSION_FILE.exists():
        print("❌  진행 중인 세션이 없습니다.  vibe start <project> <task>  로 시작하세요.")
        sys.exit(1)

    session = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    task_dir = Path(session["task_dir"])

    result_path = Path(args.file) if args.file else task_dir / "result.json"

    if not result_path.exists():
        print(f"❌  결과 파일 없음: {result_path}")
        print("   vibe prompt 로 받은 프롬프트를 Claude에 붙여넣고,")
        print("   그 JSON 결과를 result.json 에 저장하세요.")
        sys.exit(1)

    text = result_path.read_text(encoding="utf-8").strip()
    if "{" not in text or len(text) < 50:
        print("❌  result.json 에 채점 JSON이 없습니다.")
        print(f"   {result_path}  에 Claude가 출력한 JSON을 붙여넣고 저장하세요.")
        sys.exit(1)

    try:
        data = _parse_result(text)
    except Exception as e:
        print(f"❌  JSON 파싱 실패: {e}")
        print("   Claude가 출력한 JSON 전체를 빠짐없이 붙여넣었는지 확인하세요.")
        sys.exit(1)

    # 세션 메타 병합 + 합계 재계산
    data["project"] = session["project"]
    data.setdefault("task", session.get("task", ""))
    data["task"] = session.get("task", data.get("task", ""))
    data["started_at"] = session.get("started_at", "")
    data["ended_at"] = datetime.datetime.now().isoformat()
    s = data.get("scores", {})
    for k in ("one_shot", "context_drift", "ai_control", "prompt_clarity"):
        s.setdefault(k, 0)
    s["total"] = s["one_shot"] + s["context_drift"] + s["ai_control"] + s["prompt_clarity"]
    data["scores"] = s
    if not data.get("grade"):
        data["grade"] = _grade_of(s["total"])
    data.setdefault("turn_count", 0)
    data.setdefault("est_tokens", 0)

    # data.json 저장
    data_path = task_dir / "data.json"
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # report.html 생성
    html = generate_report_html(data)
    report_path = task_dir / "report.html"
    report_path.write_text(html, encoding="utf-8")

    # 전체 조회 페이지(index.html)·성장 리포트(growth.html) 갱신
    try:
        all_items = _collect_tasks()
        (ROOT / "index.html").write_text(
            generate_index_html(all_items), encoding="utf-8")
        if all_items:
            _aprojects = sorted({i["project"] for i in all_items})
            # 성능·가독성을 위해 자동 생성은 최근 기간(기본 2주)만 집계
            _cut = (datetime.datetime.now()
                    - datetime.timedelta(weeks=DEFAULT_GROWTH_WEEKS)).strftime("%Y%m%d")
            _recent = [i for i in all_items if i["date"] >= _cut] or all_items
            (ROOT / "growth.html").write_text(
                generate_growth_html(_compute_signals(_recent), _aprojects,
                                     None, DEFAULT_GROWTH_WEEKS),
                encoding="utf-8")
    except Exception:
        pass

    # 세션 파일 제거
    SESSION_FILE.unlink(missing_ok=True)

    s = data["scores"]
    grade = data["grade"]
    print(f"\n{'='*55}")
    print(f"  📊  바이브 코딩 순도 분석 완료")
    print(f"{'='*55}")
    print(f"  프로젝트  : {session['project']}")
    print(f"  작업명    : {session['task']}")
    print(f"  최종 점수 : {s['total']}/100   등급: {grade}")
    print(f"  ─────────────────────────────────")
    print(f"  원샷 달성률    : {s['one_shot']:>2}/25")
    print(f"  컨텍스트 유지  : {s['context_drift']:>2}/25")
    print(f"  주도권 제어    : {s['ai_control']:>2}/25")
    print(f"  프롬프트 선명도: {s['prompt_clarity']:>2}/25")
    tc = data.get("turn_count", 0) or 0
    et = data.get("est_tokens", 0) or 0
    if tc or et:
        print(f"  ─────────────────────────────────")
        if tc:
            print(f"  대화 턴 수     : {tc}회")
        if et:
            print(f"  추정 토큰      : ~{et:,} (추정치)")
    print(f"\n  📄  리포트: {report_path}")
    print(f"  📋  전체 조회: {ROOT / 'index.html'}  (vibe dashboard 로 언제든 열기)")
    print(f"  💡  더블클릭하면 브라우저에서 바로 열립니다!\n")


# ── vibe list ──────────────────────────────────────────────────────────────────

def _task_from_folder(name: str) -> str:
    # YYYYMMDD_HHMM_작업명 → 작업명 (구버전 YYYYMMDD_작업명 도 호환)
    parts = name.split("_")
    if len(parts) >= 3 and len(parts[1]) == 4 and parts[1].isdigit():
        return "_".join(parts[2:])
    if len(parts) >= 2:
        return "_".join(parts[1:])
    return name


def cmd_list(args):
    if not ROOT.exists():
        print("VibeGraph 데이터 없음.")
        return

    rows = []
    for proj_dir in sorted(ROOT.iterdir()):
        if not proj_dir.is_dir() or proj_dir.name.startswith("."):
            continue
        if args.project and proj_dir.name != args.project:
            continue
        for task_dir in sorted(proj_dir.iterdir(), reverse=True):
            if not task_dir.is_dir():
                continue
            data_file = task_dir / "data.json"
            if data_file.exists():
                d = json.loads(data_file.read_text(encoding="utf-8"))
                rows.append(
                    (proj_dir.name, task_dir.name[:8],
                     d.get("task") or _task_from_folder(task_dir.name),
                     d["scores"]["total"], d["grade"])
                )
            else:
                rows.append((proj_dir.name, task_dir.name[:8],
                             _task_from_folder(task_dir.name),
                             "-", "-"))

    if not rows:
        print("세션 데이터가 없습니다.")
        return

    print(f"\n  {'날짜':<10} {'프로젝트':<20} {'작업명':<30} {'점수':>5} {'등급':>4}")
    print("  " + "-" * 74)
    for proj, date, task, total, grade in rows:
        print(f"  {date:<10} {proj:<20} {task:<30} {str(total):>5} {grade:>4}")
    print()


# ── vibe stats ─────────────────────────────────────────────────────────────────

def cmd_stats(args):
    weeks = getattr(args, "weeks", 3) or 3
    cutoff = datetime.datetime.now() - datetime.timedelta(weeks=weeks)

    all_data = []
    if ROOT.exists():
        for proj_dir in ROOT.iterdir():
            if not proj_dir.is_dir() or proj_dir.name.startswith("."):
                continue
            for task_dir in proj_dir.iterdir():
                if not task_dir.is_dir():
                    continue
                data_file = task_dir / "data.json"
                if not data_file.exists():
                    continue
                try:
                    task_date = datetime.datetime.strptime(task_dir.name[:8], "%Y%m%d")
                    if task_date < cutoff:
                        continue
                except ValueError:
                    pass
                d = json.loads(data_file.read_text(encoding="utf-8"))
                d["_project"] = proj_dir.name
                all_data.append(d)

    if not all_data:
        print(f"\n  최근 {weeks}주간 분석 데이터가 없습니다.\n")
        return

    projects: dict[str, list[int]] = {}
    smell_counter: dict[str, int] = {}
    for d in all_data:
        proj = d["_project"]
        projects.setdefault(proj, []).append(d["scores"]["total"])
        for smell in d.get("prompt_smells", []):
            t = smell.get("type", "Unknown")
            smell_counter[t] = smell_counter.get(t, 0) + 1

    print(f"\n  {'='*55}")
    print(f"  📊  VibeGraph 통계  (최근 {weeks}주)")
    print(f"  {'='*55}")
    print(f"\n  [프로젝트별 평균 점수]")
    print(f"  {'프로젝트':<25} {'세션':>5} {'평균':>7}  추이")
    print("  " + "-" * 55)
    for proj, sc in sorted(projects.items()):
        avg = sum(sc) / len(sc)
        bar = "█" * int(avg / 10)
        print(f"  {proj:<25} {len(sc):>5} {avg:>6.1f}점  {bar}")

    if smell_counter:
        print(f"\n  [자주 발생한 Prompt Smell TOP 3]")
        for i, (sm, cnt) in enumerate(
            sorted(smell_counter.items(), key=lambda x: x[1], reverse=True)[:3], 1
        ):
            print(f"    {i}. {sm}: {cnt}회")

    total_sessions = len(all_data)
    overall_avg = sum(d["scores"]["total"] for d in all_data) / total_sessions
    print(f"\n  [전체 요약]")
    print(f"    총 세션: {total_sessions}개   전체 평균: {overall_avg:.1f}점\n")


# ── vibe dashboard (조회 페이지) ────────────────────────────────────────────────

def _collect_tasks() -> list:
    """모든 프로젝트/작업 폴더를 훑어 data.json 이 있는 작업들을 모은다."""
    import urllib.parse
    items = []
    if not ROOT.exists():
        return items
    for proj_dir in sorted(ROOT.iterdir()):
        if not proj_dir.is_dir() or proj_dir.name.startswith("."):
            continue
        for task_dir in sorted(proj_dir.iterdir()):
            if not task_dir.is_dir():
                continue
            data_file = task_dir / "data.json"
            report = task_dir / "report.html"
            if not data_file.exists():
                continue
            try:
                d = json.loads(data_file.read_text(encoding="utf-8"))
            except Exception:
                continue
            name = task_dir.name
            date = name[:8]
            time = name[9:13] if len(name) >= 13 and name[9:13].isdigit() else ""
            scores = d.get("scores", {})
            rel = "/".join(urllib.parse.quote(p) for p in (proj_dir.name, name, "report.html"))
            items.append({
                "project": proj_dir.name,
                "task": d.get("task") or _task_from_folder(name),
                "date": date,
                "time": time,
                "total": scores.get("total", 0),
                "grade": d.get("grade", ""),
                "turn_count": d.get("turn_count", 0) or 0,
                "est_tokens": d.get("est_tokens", 0) or 0,
                "report": rel if report.exists() else "",
                # 성장 리포트·코칭용 추가 신호
                "criteria": {k: scores.get(k, 0) for k in
                             ("one_shot", "context_drift", "ai_control", "prompt_clarity")},
                "smells": [s.get("type", "") for s in d.get("prompt_smells", []) if s.get("type")],
                "top_improvement": d.get("top_improvement", ""),
            })
    return items


# 채점 4개 항목의 한국어 라벨 (성장 리포트·코칭 공용)
_CRIT_LABELS = {
    "one_shot": "원샷 달성률",
    "context_drift": "컨텍스트 유지력",
    "ai_control": "주도권 제어력",
    "prompt_clarity": "프롬프트 선명도",
}


def generate_index_html(items: list) -> str:
    grade_color = {"S": "#10b981", "A": "#3b82f6", "B": "#f59e0b", "C": "#ef4444"}
    total_cnt = len(items)
    avg = (sum(i["total"] for i in items) / total_cnt) if total_cnt else 0
    projects = sorted({i["project"] for i in items})
    opts = "".join(f'<option value="{_esc(p)}">{_esc(p)}</option>' for p in projects)

    rows = ""
    # 최신순 정렬 (날짜+시간 내림차순)
    for it in sorted(items, key=lambda x: (x["date"], x["time"]), reverse=True):
        gc = grade_color.get(it["grade"], "#6b7280")
        d8 = it["date"]
        date_disp = f"{d8[:4]}-{d8[4:6]}-{d8[6:8]}" if len(d8) == 8 else d8
        if it["time"]:
            date_disp += f" {it['time'][:2]}:{it['time'][2:]}"
        tok = f"~{it['est_tokens']:,}" if it["est_tokens"] else "-"
        turn = f"{it['turn_count']}" if it["turn_count"] else "-"
        if it["report"]:
            task_cell = f'<a href="{it["report"]}" target="_blank">{_esc(it["task"])}</a>'
        else:
            task_cell = _esc(it["task"]) + ' <span class="norep">(리포트없음)</span>'
        rows += f"""
      <tr data-project="{_esc(it['project'])}" data-search="{_esc((it['project']+' '+it['task']).lower())}" data-total="{it['total']}" data-date="{_esc(it['date']+it['time'])}">
        <td class="c-date">{_esc(date_disp)}</td>
        <td>{_esc(it['project'])}</td>
        <td class="c-task">{task_cell}</td>
        <td class="c-num"><b style="color:{gc}">{it['total']}</b></td>
        <td class="c-grade"><span class="gb" style="background:{gc}22;color:{gc};border:1px solid {gc}66">{_esc(it['grade'])}</span></td>
        <td class="c-num">{turn}</td>
        <td class="c-num c-tok">{tok}</td>
      </tr>"""
    if not rows:
        rows = '<tr><td colspan="7" class="empty">아직 채점된 작업이 없습니다. vibe start → vibe end 로 첫 리포트를 만들어 보세요.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VibeGraph · 전체 작업 조회</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Malgun Gothic',sans-serif;background:#0f172a;color:#e2e8f0;line-height:1.5}}
a{{color:#818cf8;text-decoration:none}}
a:hover{{text-decoration:underline}}
.hd{{background:linear-gradient(135deg,#1e293b,#0f172a);padding:28px 32px;border-bottom:1px solid #334155}}
.hd h1{{font-size:24px;font-weight:800;color:#f8fafc}}
.hd .sub{{color:#94a3b8;font-size:13px;margin-top:6px}}
.wrap{{max-width:1080px;margin:0 auto;padding:26px 20px 64px}}
.cards{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}}
.kpi{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px 22px;min-width:140px}}
.kpi .v{{font-size:26px;font-weight:800;color:#f8fafc}}
.kpi .l{{font-size:12px;color:#94a3b8;margin-top:3px}}
.controls{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:14px}}
.controls input,.controls select{{background:#0b1120;border:1px solid #334155;border-radius:8px;color:#e2e8f0;padding:10px 13px;font-size:14px;font-family:inherit}}
.controls input#q{{flex:1;min-width:200px}}
.controls input::placeholder{{color:#475569}}
.controls input[type=date]{{color-scheme:dark;width:155px}}
.controls .tilde{{color:#475569}}
.controls button{{background:#334155;color:#cbd5e1;border:none;border-radius:8px;padding:10px 14px;font-size:13px;cursor:pointer;font-family:inherit}}
.controls button:hover{{background:#475569}}
.kpi.filt .v{{color:#a5b4fc}}
table{{width:100%;border-collapse:collapse;background:#1e293b;border:1px solid #334155;border-radius:12px;overflow:hidden}}
th,td{{text-align:left;padding:11px 14px;border-bottom:1px solid #293548;font-size:13px}}
th{{color:#94a3b8;font-weight:600;cursor:pointer;user-select:none;white-space:nowrap}}
th:hover{{color:#cbd5e1}}
th.c-num,td.c-num{{text-align:right}}
th.c-grade,td.c-grade{{text-align:center}}
tr:last-child td{{border-bottom:none}}
tbody tr:hover{{background:#26334a}}
.c-task{{max-width:340px}}
.c-tok{{color:#64748b}}
.gb{{display:inline-block;min-width:26px;text-align:center;padding:2px 8px;border-radius:6px;font-weight:800;font-size:12px}}
.norep{{color:#475569;font-size:11px}}
.empty{{text-align:center;color:#475569;padding:30px}}
.foot{{text-align:center;color:#475569;font-size:12px;margin-top:34px}}
.count{{color:#64748b;font-size:12px;margin:10px 2px}}
</style>
</head>
<body>
<div class="hd">
  <h1>🎯 VibeGraph · 전체 작업 조회</h1>
  <div class="sub">채점된 모든 작업을 한 눈에. 작업명을 클릭하면 해당 리포트가 열립니다.
    &nbsp;·&nbsp; <a href="growth.html">📈 성장 리포트 →</a></div>
</div>
<div class="wrap">
  <div class="cards">
    <div class="kpi filt"><div class="v" id="k-cnt">{total_cnt}</div><div class="l">작업 수 (검색 결과)</div></div>
    <div class="kpi filt"><div class="v" id="k-avg">{avg:.1f}</div><div class="l">평균 점수 (검색 결과)</div></div>
    <div class="kpi filt"><div class="v" id="k-proj">{len(projects)}</div><div class="l">프로젝트 수 (검색 결과)</div></div>
  </div>

  <div class="controls">
    <input id="q" type="text" placeholder="🔍 프로젝트·작업명 검색…">
    <select id="pf"><option value="">전체 프로젝트</option>{opts}</select>
    <input id="d1" type="date" title="시작일">
    <span class="tilde">~</span>
    <input id="d2" type="date" title="종료일">
    <button id="clr" type="button">초기화</button>
  </div>
  <div class="count" id="cnt"></div>

  <table id="tbl">
    <thead>
      <tr>
        <th data-sort="date">날짜 ▾</th>
        <th data-sort="project">프로젝트</th>
        <th data-sort="task">작업명</th>
        <th class="c-num" data-sort="total">점수</th>
        <th class="c-grade" data-sort="total">등급</th>
        <th class="c-num" data-sort="turn">턴</th>
        <th class="c-num" data-sort="tok">추정토큰</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="foot">VibeGraph · 바이브코딩을 엔지니어링으로</div>
</div>
<script>
var tbody=document.querySelector('#tbl tbody');
var rowsAll=[].slice.call(tbody.querySelectorAll('tr')).filter(function(r){{return r.dataset.search!==undefined}});
var q=document.getElementById('q'),pf=document.getElementById('pf'),cnt=document.getElementById('cnt');
var d1=document.getElementById('d1'),d2=document.getElementById('d2'),clr=document.getElementById('clr');
var kCnt=document.getElementById('k-cnt'),kAvg=document.getElementById('k-avg'),kProj=document.getElementById('k-proj');
function apply(){{
  var t=(q.value||'').toLowerCase().trim(), p=pf.value;
  var a=(d1.value||'').replace(/-/g,''), b=(d2.value||'').replace(/-/g,'');
  var n=0, sum=0, projset={{}};
  rowsAll.forEach(function(r){{
    var d8=r.dataset.date.slice(0,8);
    var ok=(!t||r.dataset.search.indexOf(t)>=0)&&(!p||r.dataset.project===p)
           &&(!a||d8>=a)&&(!b||d8<=b);
    r.style.display=ok?'':'none';
    if(ok){{n++; sum+=+r.dataset.total; projset[r.dataset.project]=1;}}
  }});
  kCnt.textContent=n;
  kAvg.textContent=n?(sum/n).toFixed(1):'0.0';
  kProj.textContent=Object.keys(projset).length;
  cnt.textContent=n+'개 표시됨';
}}
q.addEventListener('input',apply); pf.addEventListener('change',apply);
d1.addEventListener('change',apply); d2.addEventListener('change',apply);
clr.addEventListener('click',function(){{q.value='';pf.value='';d1.value='';d2.value='';apply();}});
var asc={{}};
document.querySelectorAll('th[data-sort]').forEach(function(th){{
  th.addEventListener('click',function(){{
    var k=th.dataset.sort; asc[k]=!asc[k]; var dir=asc[k]?1:-1;
    var arr=rowsAll.slice();
    arr.sort(function(a,b){{
      var x,y;
      if(k==='total'){{x=+a.dataset.total;y=+b.dataset.total;}}
      else if(k==='date'){{x=a.dataset.date;y=b.dataset.date;}}
      else if(k==='turn'){{x=+(a.children[5].textContent.replace('-','0'));y=+(b.children[5].textContent.replace('-','0'));}}
      else if(k==='tok'){{x=+(a.children[6].textContent.replace(/[^0-9]/g,'')||0);y=+(b.children[6].textContent.replace(/[^0-9]/g,'')||0);}}
      else {{x=a.dataset.search;y=b.dataset.search;}}
      return x<y?-dir:x>y?dir:0;
    }});
    arr.forEach(function(r){{tbody.appendChild(r);}});
  }});
}});
apply();
</script>
</body>
</html>"""


def cmd_dashboard(args):
    items = _collect_tasks()
    out = ROOT / "index.html"
    out.write_text(generate_index_html(items), encoding="utf-8")
    print(f"\n📋  전체 조회 페이지 생성: {out}")
    print(f"   채점된 작업 {len(items)}개")
    print(f"   💡 더블클릭하면 브라우저에서 열립니다. (작업명 클릭 → 개별 리포트)\n")
    if not getattr(args, "no_open", False):
        _open_path(out)


# ── 성장 분석 신호 추출 (A·B 공용) ───────────────────────────────────────────────

def _compute_signals(items: list) -> dict:
    """채점된 작업들에서 결정론적 신호를 뽑는다(환각 없는 순수 계산)."""
    ordered = sorted(items, key=lambda x: (x["date"], x["time"]))
    n = len(ordered)
    totals = [i["total"] for i in ordered]
    overall = sum(totals) / n if n else 0

    # 항목별 평균
    crit_avg = {}
    for k in _CRIT_LABELS:
        vals = [i["criteria"].get(k, 0) for i in ordered]
        crit_avg[k] = sum(vals) / n if n else 0
    weakest = min(crit_avg, key=crit_avg.get) if crit_avg else None
    strongest = max(crit_avg, key=crit_avg.get) if crit_avg else None

    # 추세: 전반부 vs 후반부 평균
    trend_delta = 0.0
    if n >= 4:
        half = n // 2
        early = sum(totals[:half]) / half
        late = sum(totals[half:]) / (n - half)
        trend_delta = late - early

    # 반복 스멜 집계
    smell_counts: dict = {}
    for i in ordered:
        for s in i["smells"]:
            smell_counts[s] = smell_counts.get(s, 0) + 1
    smell_top = sorted(smell_counts.items(), key=lambda x: x[1], reverse=True)

    # 프로젝트별 평균
    proj_tot: dict = {}
    for i in ordered:
        proj_tot.setdefault(i["project"], []).append(i["total"])
    proj_avg = {p: sum(v) / len(v) for p, v in proj_tot.items()}

    # 등급 분포
    grade_dist: dict = {}
    for i in ordered:
        g = i["grade"] or "?"
        grade_dist[g] = grade_dist.get(g, 0) + 1

    # 최근 개선포인트(중복 제거, 최신순 최대 5)
    seen, recent_imp = set(), []
    for i in reversed(ordered):
        ti = (i["top_improvement"] or "").strip()
        if ti and ti not in seen:
            seen.add(ti)
            recent_imp.append(ti)
        if len(recent_imp) >= 5:
            break

    return {
        "n": n, "overall": overall, "ordered": ordered, "totals": totals,
        "crit_avg": crit_avg, "weakest": weakest, "strongest": strongest,
        "trend_delta": trend_delta, "smell_top": smell_top,
        "proj_avg": proj_avg, "grade_dist": grade_dist, "recent_imp": recent_imp,
    }


# ── (A) vibe growth — 결정론적 성장 리포트 ──────────────────────────────────────

# 성장 리포트 기본 분석 기간(주). vibe end 자동 생성·vibe growth 기본값에 사용.
# 전체를 기본으로 하면 작업이 쌓일수록 느려지고 추세 차트도 복잡해지므로 최근 기간으로 제한.
DEFAULT_GROWTH_WEEKS = 2


def _q(name: str) -> str:
    """명령어용: 공백 있으면 따옴표로 감싼다."""
    return f'"{name}"' if (" " in name) else name


def generate_growth_html(sig: dict, all_projects=None, sel_project=None, weeks=None) -> str:
    n = sig["n"]
    overall = sig["overall"]
    all_projects = all_projects or []

    # 현재 필터 배너
    fparts = []
    if sel_project:
        fparts.append(f"프로젝트 <b>{_esc(sel_project)}</b>")
    if weeks:
        fparts.append(f"최근 <b>{weeks}주</b>")
    filter_banner = ("🔎 현재 조건: " + " · ".join(fparts)) if fparts else "📚 전체 누적"

    # 다른 조건으로 보기 — 복사 가능한 명령어 목록
    cmds = [(f"최근 {DEFAULT_GROWTH_WEEKS}주 (기본값)", "vibe growth"),
            ("전체 기간", "vibe growth --all")]
    for p in all_projects:
        cmds.append((f"프로젝트: {p} (전체)", f"vibe growth --project {_q(p)} --all"))
    for w in (4, 8, 12):
        cmds.append((f"최근 {w}주", f"vibe growth --weeks {w}"))
    if sel_project:
        cmds.append((f"{sel_project} · 최근 8주",
                     f"vibe growth --project {_q(sel_project)} --weeks 8"))
    cmd_rows = ""
    for idx, (label, cmd) in enumerate(cmds):
        cmd_rows += (
            f'<div class="gcmd"><span class="gcmd-lbl">{_esc(label)}</span>'
            f'<code id="gc{idx}">{_esc(cmd)}</code>'
            f'<button class="gcopy" data-t="gc{idx}">복사</button></div>'
        )
    delta = sig["trend_delta"]
    if delta > 1:
        trend_txt, trend_col = f"▲ +{delta:.1f}", "#10b981"
    elif delta < -1:
        trend_txt, trend_col = f"▼ {delta:.1f}", "#ef4444"
    else:
        trend_txt, trend_col = "→ 변화 적음", "#94a3b8"

    ordered = sig["ordered"]
    labels = json.dumps([f"{i['date'][4:6]}/{i['date'][6:8]}" for i in ordered])
    totals_js = json.dumps(sig["totals"])

    # 항목별 평균 막대
    crit_rows = ""
    for k, lbl in _CRIT_LABELS.items():
        v = sig["crit_avg"].get(k, 0)
        is_weak = (k == sig["weakest"])
        col = "#ef4444" if is_weak else "#6366f1"
        tag = ' <span style="color:#f87171;font-size:11px">← 가장 약함</span>' if is_weak else ""
        crit_rows += f"""
      <div class="srow"><span class="slbl">{lbl}{tag}</span>
        <div class="sbw"><div class="sb" style="width:{v/25*100:.0f}%;background:{col}"></div></div>
        <span class="sval">{v:.1f}/25</span></div>"""

    # 반복 스멜
    smell_rows = ""
    for sm, cnt in sig["smell_top"][:5]:
        smell_rows += f'<div class="line"><span>{_esc(sm)}</span><b>{cnt}회</b></div>'
    if not smell_rows:
        smell_rows = '<p class="empty">반복된 Prompt Smell 없음 👍</p>'

    # 프로젝트 평균
    proj_rows = ""
    for p, v in sorted(sig["proj_avg"].items(), key=lambda x: x[1], reverse=True):
        proj_rows += f'<div class="line"><span>{_esc(p)}</span><b>{v:.1f}점</b></div>'

    # 등급 분포
    grade_rows = ""
    for g in ("S", "A", "B", "C"):
        if sig["grade_dist"].get(g):
            grade_rows += f'<div class="line"><span>{g}등급</span><b>{sig["grade_dist"][g]}회</b></div>'

    weak_lbl = _CRIT_LABELS.get(sig["weakest"], "-") if sig["weakest"] else "-"
    imp_rows = "".join(f"<li>{_esc(t)}</li>" for t in sig["recent_imp"]) or "<li class='empty'>기록 없음</li>"

    return f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>VibeGraph · 성장 리포트</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Malgun Gothic',sans-serif;background:#0f172a;color:#e2e8f0;line-height:1.5}}
a{{color:#818cf8}}
.hd{{background:linear-gradient(135deg,#1e293b,#0f172a);padding:28px 32px;border-bottom:1px solid #334155}}
.hd h1{{font-size:24px;font-weight:800;color:#f8fafc}}
.hd .sub{{color:#94a3b8;font-size:13px;margin-top:6px}}
.wrap{{max-width:1000px;margin:0 auto;padding:26px 20px 64px}}
.cards{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:22px}}
.kpi{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:16px 22px;min-width:150px}}
.kpi .v{{font-size:26px;font-weight:800;color:#f8fafc}}
.kpi .l{{font-size:12px;color:#94a3b8;margin-top:3px}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:18px}}
@media(max-width:720px){{.g2{{grid-template-columns:1fr}}}}
.card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:22px}}
.card h3{{font-size:15px;font-weight:600;color:#f8fafc;margin-bottom:14px}}
.srow{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.slbl{{font-size:12px;color:#94a3b8;width:175px;flex-shrink:0}}
.sbw{{flex:1;background:#334155;border-radius:4px;height:8px;overflow:hidden}}
.sb{{height:100%;border-radius:4px}}
.sval{{font-size:13px;font-weight:600;color:#f8fafc;width:54px;text-align:right}}
.line{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #293548;font-size:13px;color:#cbd5e1}}
.line:last-child{{border-bottom:none}} .line b{{color:#f8fafc}}
.focus{{background:#ef444415;border:1px solid #ef444440;border-radius:10px;padding:16px 18px;margin-bottom:18px}}
.focus b{{color:#fca5a5}}
.imp{{margin:8px 0 0 18px;color:#cbd5e1;font-size:13px}} .imp li{{margin-bottom:5px}}
.empty{{color:#475569;font-size:13px}}
canvas{{max-height:240px}}
.fbar{{display:inline-block;background:#6366f118;border:1px solid #6366f140;color:#c7d2fe;border-radius:8px;padding:6px 14px;font-size:13px;margin-bottom:18px}}
.gcmd{{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid #293548;font-size:13px}}
.gcmd:last-child{{border-bottom:none}}
.gcmd-lbl{{color:#94a3b8;width:130px;flex-shrink:0}}
.gcmd code{{flex:1;background:#0b1120;border:1px solid #334155;border-radius:6px;padding:6px 10px;color:#a5b4fc;font-family:'Consolas',monospace;font-size:12.5px;overflow-x:auto;white-space:nowrap}}
.gcopy{{flex-shrink:0;background:#334155;color:#cbd5e1;border:none;border-radius:6px;padding:6px 11px;font-size:12px;cursor:pointer;font-family:inherit}}
.gcopy:hover{{background:#475569}}
.gcopy.done{{background:#10b981;color:#fff}}
.foot{{text-align:center;color:#475569;font-size:12px;margin-top:34px}}
</style></head><body>
<div class="hd">
  <h1>📈 VibeGraph · 성장 리포트</h1>
  <div class="sub">최근 {n}개 작업을 누적 분석했습니다. (순수 계산 기반 — 해석은 vibe coach 참고)
    &nbsp;·&nbsp; <a href="index.html">📋 전체 작업 조회 →</a></div>
</div>
<div class="wrap">
  <div class="fbar">{filter_banner}</div>
  <div class="cards">
    <div class="kpi"><div class="v">{n}</div><div class="l">작업 수</div></div>
    <div class="kpi"><div class="v">{overall:.1f}</div><div class="l">전체 평균 점수</div></div>
    <div class="kpi"><div class="v" style="color:{trend_col}">{trend_txt}</div><div class="l">추세(전반부→후반부)</div></div>
  </div>

  <div class="focus">🎯 <b>지금 가장 집중할 항목: {weak_lbl}</b> — 네 작업에서 평균적으로 가장 낮은 점수대 영역입니다.</div>

  <div class="card" style="margin-bottom:18px">
    <h3>📉 점수 추이</h3>
    <canvas id="tc"></canvas>
  </div>

  <div class="g2">
    <div class="card"><h3>📊 항목별 평균</h3>{crit_rows}</div>
    <div class="card"><h3>🛑 반복된 Prompt Smell</h3>{smell_rows}</div>
  </div>
  <div class="g2">
    <div class="card"><h3>📁 프로젝트별 평균</h3>{proj_rows or '<p class=empty>데이터 없음</p>'}</div>
    <div class="card"><h3>🏅 등급 분포</h3>{grade_rows or '<p class=empty>데이터 없음</p>'}</div>
  </div>

  <div class="card" style="margin-top:18px">
    <h3>🔑 최근 개선포인트 모음</h3>
    <ul class="imp">{imp_rows}</ul>
  </div>

  <div class="card" style="margin-top:18px">
    <h3>🔎 다른 조건으로 보기 <span style="font-weight:400;color:#64748b;font-size:12px">— 복사해서 터미널에 붙여넣으면 그 조건으로 다시 만듭니다</span></h3>
    <p style="color:#64748b;font-size:12px;margin-bottom:8px">ℹ 작업이 끝날 때(<b>vibe end</b>) 자동 생성되는 이 페이지는 <b>최근 {DEFAULT_GROWTH_WEEKS}주</b>만 집계합니다(속도·가독성). 전체를 보려면 <b>vibe growth --all</b>.</p>
    {cmd_rows}
  </div>

  <div class="foot">VibeGraph · 바이브코딩을 엔지니어링으로</div>
</div>
<script>
document.querySelectorAll('.gcopy').forEach(function(b){{
  b.addEventListener('click',function(){{
    var t=document.getElementById(b.dataset.t).innerText;
    navigator.clipboard.writeText(t).then(function(){{
      b.textContent='복사됨'; b.classList.add('done');
      setTimeout(function(){{b.textContent='복사'; b.classList.remove('done');}},1500);
    }});
  }});
}});
new Chart(document.getElementById('tc'),{{
  type:'line',
  data:{{labels:{labels},datasets:[{{label:'총점',data:{totals_js},borderColor:'#6366f1',backgroundColor:'#6366f133',fill:true,tension:.3,pointRadius:4}}]}},
  options:{{plugins:{{legend:{{display:false}}}},scales:{{y:{{min:0,max:100,ticks:{{color:'#94a3b8'}},grid:{{color:'#293548'}}}},x:{{ticks:{{color:'#94a3b8'}},grid:{{display:false}}}}}}}}
}});
</script>
</body></html>"""


def cmd_growth(args):
    items = _collect_tasks()
    if not items:
        print("\n아직 채점된 작업이 없습니다. vibe start → vibe end 후 다시 시도하세요.\n")
        return
    all_projects = sorted({i["project"] for i in items})

    sel_project = getattr(args, "project", None)
    # 기간 결정: --all 이면 전체, --weeks N 이면 N주, 아니면 기본 2주
    if getattr(args, "all", False):
        weeks = None
    elif getattr(args, "weeks", None):
        weeks = args.weeks
    else:
        weeks = DEFAULT_GROWTH_WEEKS

    flt = items
    if sel_project:
        flt = [i for i in flt if i["project"] == sel_project]
    if weeks:
        cutoff = (datetime.datetime.now() - datetime.timedelta(weeks=weeks)).strftime("%Y%m%d")
        flt = [i for i in flt if i["date"] >= cutoff]

    if not flt:
        cond = []
        if sel_project:
            cond.append(f"프로젝트={sel_project}")
        if weeks:
            cond.append(f"최근{weeks}주")
        print(f"\n해당 조건({', '.join(cond)})에 맞는 작업이 없습니다.")
        if weeks:
            print(f"   전체 기간을 보려면:  vibe growth --all")
        if all_projects:
            print(f"   사용 가능한 프로젝트: {', '.join(all_projects)}")
        print()
        return

    sig = _compute_signals(flt)
    out = ROOT / "growth.html"
    out.write_text(generate_growth_html(sig, all_projects, sel_project, weeks), encoding="utf-8")
    cond_txt = ""
    if sel_project or weeks:
        bits = ([f"프로젝트 {sel_project}"] if sel_project else []) + ([f"최근 {weeks}주"] if weeks else [])
        cond_txt = f"  [조건: {' · '.join(bits)}]"
    print(f"\n📈  성장 리포트 생성: {out}{cond_txt}")
    print(f"   {sig['n']}개 · 평균 {sig['overall']:.1f}점 · "
          f"가장 약한 항목: {_CRIT_LABELS.get(sig['weakest'],'-')}")
    print(f"   💡 더블클릭하면 브라우저에서 열립니다. (다른 조건 명령은 페이지 하단에서 복사)\n")
    if not getattr(args, "no_open", False):
        _open_path(out)


# ── (B) vibe coach — 추출 신호 기반 코칭 프롬프트 ───────────────────────────────

COACH_MIN_SESSIONS = 4


def _build_coach_prompt(sig: dict) -> str:
    lines = []
    lines.append(f"- 누적 작업 수: {sig['n']}개,  전체 평균: {sig['overall']:.1f}/100")
    d = sig["trend_delta"]
    arrow = "상승" if d > 1 else ("하락" if d < -1 else "정체")
    lines.append(f"- 점수 추세(전반부→후반부): {d:+.1f}점 ({arrow})")
    lines.append("- 항목별 평균(각 25점 만점):")
    for k, lbl in _CRIT_LABELS.items():
        mark = "  ← 최저" if k == sig["weakest"] else ("  ← 최고" if k == sig["strongest"] else "")
        lines.append(f"    · {lbl}: {sig['crit_avg'][k]:.1f}{mark}")
    if sig["smell_top"]:
        sm = ", ".join(f"{t}({c}회)" for t, c in sig["smell_top"][:5])
        lines.append(f"- 반복된 Prompt Smell: {sm}")
    else:
        lines.append("- 반복된 Prompt Smell: 없음")
    if sig["proj_avg"]:
        pj = ", ".join(f"{p} {v:.0f}점" for p, v in
                       sorted(sig["proj_avg"].items(), key=lambda x: x[1], reverse=True))
        lines.append(f"- 프로젝트별 평균: {pj}")
    if sig["recent_imp"]:
        lines.append("- 과거 리포트가 지목한 개선포인트들:")
        for t in sig["recent_imp"]:
            lines.append(f"    · {t}")
    signals_block = "\n".join(lines)

    return f"""너는 시니어 프롬프트 엔지니어이자 바이브코딩 코치다.
아래는 한 개발자의 최근 작업들을 채점해 "계산으로 뽑아낸 누적 신호"다.
(개별 대화 원문은 없다. 아래 수치만 근거로 삼아라. 수치에 없는 내용을 지어내지 마라.)

[누적 신호]
{signals_block}

[지시]
위 수치만 근거로, 이 개발자의 "반복되는 약점 1~2개"와 "다음 작업에서 당장 실천할 구체적 행동 2~3개"를 코칭해라.
- 일반론("계속 잘하세요")은 금지. 반드시 위 수치(최저 항목·반복 스멜·추세)에 연결해 말하라.
- 근거가 약하면 솔직히 "데이터가 적어 단정 어렵다"고 말해도 된다. 억지 분석 금지.
- 마지막에 한 줄로 "이번 주 한 가지 실험" 형태의 행동 과제를 제시하라.
- 분량은 한국어 8~12줄 이내. 표·코드블록 없이 담백하게."""


def cmd_coach(args):
    items = _collect_tasks()
    n = len(items)
    if n == 0:
        print("\n아직 채점된 작업이 없습니다. 먼저 작업을 쌓으세요.\n")
        return
    if n < COACH_MIN_SESSIONS:
        print(f"\n⚠  현재 누적 작업이 {n}개뿐입니다. "
              f"코칭은 {COACH_MIN_SESSIONS}개 이상부터 의미가 있습니다.")
        print(f"   (그래도 진행은 합니다 — 데이터가 적으면 코치가 '단정 어렵다'고 답할 수 있어요)")
    sig = _compute_signals(items)
    prompt = _build_coach_prompt(sig)
    _copy_to_clipboard(prompt)
    print(f"\n🧭  누적 코칭 프롬프트를 클립보드에 복사했습니다. (작업 {n}개 기반)")
    print(f"   → 평소 쓰던 Claude Code 창에 붙여넣기(Ctrl+V) 하면,")
    print(f"     계산된 신호를 바탕으로 한 맞춤 코칭을 받습니다. (API 불필요)")
    print(f"   ※ 개별 작업 채점과 달리, 이건 '누적 패턴'에 대한 코칭입니다.\n")
    print("─" * 55)
    print(prompt)
    print("─" * 55 + "\n")


# ── 결과 JSON 파싱 ──────────────────────────────────────────────────────────────

def _grade_of(total: int) -> str:
    if total >= 92:
        return "S"
    if total >= 82:
        return "A"
    if total >= 70:
        return "B"
    return "C"


def _parse_result(text: str) -> dict:
    """Claude가 붙여넣은 응답에서 JSON 한 덩어리를 추출해 파싱한다.
    ```json 펜스나 앞뒤 설명 문장이 섞여 있어도 견디도록 처리."""
    import re
    raw = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", raw, re.S)
    if m:
        raw = m.group(1).strip()
    if not raw.startswith("{"):
        i, j = raw.find("{"), raw.rfind("}")
        if i != -1 and j != -1 and j > i:
            raw = raw[i:j + 1]
    return json.loads(raw)


# ── HTML 리포트 생성 ────────────────────────────────────────────────────────────

def _esc(s: str) -> str:
    """HTML 특수문자 이스케이프"""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def generate_report_html(data: dict) -> str:
    scores = data["scores"]
    grade = data["grade"]
    grade_color = {"S": "#10b981", "A": "#3b82f6", "B": "#f59e0b", "C": "#ef4444"}.get(grade, "#6b7280")

    turn_purity = data.get("turn_purity", [50])
    turn_labels_js = json.dumps([f"T{i+1}" for i in range(len(turn_purity))])
    turn_purity_js = json.dumps(turn_purity)

    # Prompt Smell 카드
    smells_html = ""
    for smell in data.get("prompt_smells", []):
        smells_html += f"""
      <div class="smell-card">
        <div class="smell-header">
          <span class="smell-type">{_esc(smell.get("type",""))}</span>
          <span class="wasted">⏱ {smell.get("wasted_turns",0)}턴 낭비</span>
        </div>
        <div class="smell-ctx">{_esc(smell.get("turn_desc",""))}</div>
        <div class="smell-desc">{_esc(smell.get("description",""))}</div>
      </div>"""
    if not smells_html:
        smells_html = '<p class="empty">감지된 Prompt Smell 없음 👍</p>'

    # Good/Bad 예시 카드
    examples_html = ""
    for ex in data.get("good_bad_examples", []):
        examples_html += f"""
      <div class="ex-card">
        <div class="ex-ctx">💬 {_esc(ex.get("context",""))}</div>
        <div class="ex-cols">
          <div class="bad-box">
            <div class="box-lbl">❌ Bad</div>
            <pre class="box-content">{_esc(ex.get("bad",""))}</pre>
          </div>
          <div class="good-box">
            <div class="box-lbl">✅ Good</div>
            <pre class="box-content">{_esc(ex.get("good",""))}</pre>
          </div>
        </div>
        <div class="ex-effect">🎯 기대 효과: {_esc(ex.get("expected_effect",""))}</div>
      </div>"""
    if not examples_html:
        examples_html = '<p class="empty">예시 데이터 없음</p>'

    # 도구/스킬 추천 카드
    skills_html = ""
    for sk in data.get("skill_recommendations", []):
        skills_html += f"""
      <div class="skill-card">
        <div class="skill-sit">🧭 {_esc(sk.get("situation",""))}</div>
        <div class="skill-row"><span class="skill-lbl used">지금</span><span>{_esc(sk.get("used_approach",""))}</span></div>
        <div class="skill-row"><span class="skill-lbl rec">추천</span><span>{_esc(sk.get("better_skill",""))}</span></div>
        <div class="skill-reason">💡 {_esc(sk.get("reason",""))}</div>
      </div>"""
    if not skills_html:
        skills_html = '<p class="empty">추천할 대체 스킬 없음 — 도구 선택이 적절했습니다 👍</p>'

    ended = data.get("ended_at", "")[:16].replace("T", " ")

    # 대화 턴 수 · 추정 토큰 칩
    turn_count = data.get("turn_count", 0) or 0
    est_tokens = data.get("est_tokens", 0) or 0
    chips = []
    if turn_count:
        chips.append(f'<div class="chip">🔁 대화 턴 <b>{turn_count}</b>회</div>')
    if est_tokens:
        chips.append(f'<div class="chip">🪙 추정 토큰 <b>~{est_tokens:,}</b> <span class="est">(추정치)</span></div>')
    chips_html = f'<div class="chips">{"".join(chips)}</div>' if chips else ""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VibeGraph · {_esc(data.get("project",""))} / {_esc(data.get("task",""))}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}}
a{{color:#818cf8}}
.hd{{background:linear-gradient(135deg,#1e293b,#0f172a);padding:28px 32px;border-bottom:1px solid #334155}}
.hd h1{{font-size:22px;font-weight:700;color:#f8fafc}}
.hd .meta{{color:#94a3b8;font-size:13px;margin-top:5px}}
.wrap{{max-width:1080px;margin:0 auto;padding:28px 20px}}
.grade-banner{{background:{grade_color}18;border:2px solid {grade_color};border-radius:14px;padding:22px 28px;margin-bottom:28px;display:flex;align-items:center;gap:20px}}
.grade-letter{{font-size:60px;font-weight:900;color:{grade_color};line-height:1;flex-shrink:0}}
.grade-info h2{{font-size:18px;color:#f8fafc}}
.grade-info p{{color:#94a3b8;font-size:13px;margin-top:4px}}
.total{{font-size:38px;font-weight:700;color:{grade_color};margin-left:auto}}
.total span{{font-size:15px;color:#94a3b8}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px}}
@media(max-width:680px){{.g2{{grid-template-columns:1fr}}}}
.card{{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:22px}}
.card h3{{font-size:15px;font-weight:600;color:#f8fafc;margin-bottom:14px}}
.srow{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.slbl{{font-size:12px;color:#94a3b8;width:130px;flex-shrink:0}}
.sbw{{flex:1;background:#334155;border-radius:4px;height:7px;overflow:hidden}}
.sb{{height:100%;border-radius:4px;background:linear-gradient(90deg,#3b82f6,#8b5cf6)}}
.sval{{font-size:13px;font-weight:600;color:#f8fafc;width:38px;text-align:right}}
.summary-card{{background:#1e293b;border:1px solid #4f46e540;border-radius:12px;padding:20px;margin-bottom:28px}}
.summary-card p{{color:#cbd5e1;line-height:1.65;font-size:14px}}
.tip{{background:#f59e0b18;border:1px solid #f59e0b40;border-radius:8px;padding:10px 14px;margin-top:12px;font-size:13px}}
.tip strong{{color:#fbbf24}}
.sec-title{{font-size:17px;font-weight:700;color:#f8fafc;margin:28px 0 14px;border-left:3px solid #6366f1;padding-left:11px}}
.smell-card{{background:#0f172a;border:1px solid #ef444430;border-radius:8px;padding:14px;margin-bottom:10px}}
.smell-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:7px}}
.smell-type{{background:#ef444420;color:#f87171;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700}}
.wasted{{color:#f59e0b;font-size:12px}}
.smell-ctx{{color:#64748b;font-size:12px;margin-bottom:3px}}
.smell-desc{{color:#cbd5e1;font-size:13px}}
.ex-card{{background:#0f172a;border:1px solid #334155;border-radius:10px;padding:18px;margin-bottom:14px}}
.ex-ctx{{color:#94a3b8;font-size:13px;margin-bottom:12px}}
.ex-cols{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:10px}}
@media(max-width:600px){{.ex-cols{{grid-template-columns:1fr}}}}
.bad-box,.good-box{{border-radius:8px;padding:12px}}
.bad-box{{background:#ef444412;border:1px solid #ef444435}}
.good-box{{background:#10b98112;border:1px solid #10b98135}}
.box-lbl{{font-size:11px;font-weight:700;margin-bottom:6px}}
.bad-box .box-lbl{{color:#f87171}}
.good-box .box-lbl{{color:#34d399}}
.box-content{{font-size:12px;color:#cbd5e1;white-space:pre-wrap;font-family:inherit;line-height:1.5}}
.ex-effect{{font-size:12px;color:#a78bfa}}
.skill-card{{background:#0f172a;border:1px solid #6366f140;border-radius:10px;padding:16px;margin-bottom:12px}}
.skill-sit{{color:#e2e8f0;font-size:13px;font-weight:600;margin-bottom:10px}}
.skill-row{{display:flex;gap:9px;align-items:flex-start;margin-bottom:6px;font-size:13px;color:#cbd5e1}}
.skill-lbl{{flex-shrink:0;font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px;margin-top:1px}}
.skill-lbl.used{{background:#64748b25;color:#94a3b8}}
.skill-lbl.rec{{background:#6366f125;color:#a5b4fc}}
.skill-reason{{font-size:12px;color:#818cf8;margin-top:6px;padding-top:7px;border-top:1px solid #1e293b}}
.empty{{color:#475569;font-size:13px;padding:8px 0}}
.chips{{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:28px}}
.chip{{background:#1e293b;border:1px solid #334155;border-radius:999px;padding:8px 16px;font-size:13px;color:#cbd5e1;display:flex;align-items:center;gap:7px}}
.chip b{{color:#f8fafc;font-weight:700}}
.chip .est{{color:#64748b;font-size:11px}}
canvas{{max-height:210px}}
</style>
</head>
<body>
<div class="hd">
  <h1>🎯 VibeGraph Report</h1>
  <div class="meta">{_esc(data.get("project",""))} / {_esc(data.get("task",""))} &nbsp;·&nbsp; {_esc(ended)}</div>
</div>
<div class="wrap">

  <div class="grade-banner">
    <div class="grade-letter">{grade}</div>
    <div class="grade-info">
      <h2>바이브 코딩 순도 등급</h2>
      <p>{_esc(data.get("grade_reason",""))}</p>
    </div>
    <div class="total">{scores["total"]}<span>/100</span></div>
  </div>

  {chips_html}

  <div class="summary-card">
    <p>{_esc(data.get("summary",""))}</p>
    <div class="tip">🔑 <strong>핵심 개선 포인트:</strong> {_esc(data.get("top_improvement",""))}</div>
  </div>

  <div class="g2">
    <div class="card">
      <h3>📊 세부 점수</h3>
      <div class="srow"><span class="slbl">원샷 달성률</span>
        <div class="sbw"><div class="sb" style="width:{scores['one_shot']/25*100:.0f}%"></div></div>
        <span class="sval">{scores["one_shot"]}/25</span></div>
      <div class="srow"><span class="slbl">컨텍스트 유지력</span>
        <div class="sbw"><div class="sb" style="width:{scores['context_drift']/25*100:.0f}%"></div></div>
        <span class="sval">{scores["context_drift"]}/25</span></div>
      <div class="srow"><span class="slbl">주도권 제어력</span>
        <div class="sbw"><div class="sb" style="width:{scores['ai_control']/25*100:.0f}%"></div></div>
        <span class="sval">{scores["ai_control"]}/25</span></div>
      <div class="srow"><span class="slbl">프롬프트 선명도</span>
        <div class="sbw"><div class="sb" style="width:{scores['prompt_clarity']/25*100:.0f}%"></div></div>
        <span class="sval">{scores["prompt_clarity"]}/25</span></div>
    </div>
    <div class="card">
      <h3>📈 레이더 차트</h3>
      <canvas id="rc"></canvas>
    </div>
  </div>

  <div class="card" style="margin-bottom:24px">
    <h3>📉 대화 흐름별 순도 추이</h3>
    <canvas id="tc"></canvas>
  </div>

  <div class="sec-title">🛑 Prompt Smell 감지</div>
  {smells_html}

  <div class="sec-title">💡 프롬프트 리팩토링 가이드</div>
  {examples_html}

  <div class="sec-title">🧭 더 나은 도구·스킬 추천</div>
  {skills_html}

</div>
<script>
new Chart(document.getElementById('rc'),{{
  type:'radar',
  data:{{
    labels:['원샷 달성률','컨텍스트 유지','주도권 제어','프롬프트 선명도'],
    datasets:[{{
      data:[{scores["one_shot"]},{scores["context_drift"]},{scores["ai_control"]},{scores["prompt_clarity"]}],
      backgroundColor:'rgba(99,102,241,0.18)',
      borderColor:'#6366f1',borderWidth:2,pointBackgroundColor:'#6366f1'
    }}]
  }},
  options:{{
    responsive:true,
    scales:{{r:{{min:0,max:25,ticks:{{stepSize:5,color:'#94a3b8',backdropColor:'transparent'}},
      grid:{{color:'#334155'}},pointLabels:{{color:'#94a3b8',font:{{size:11}}}}}}
    }},
    plugins:{{legend:{{display:false}}}}
  }}
}});
new Chart(document.getElementById('tc'),{{
  type:'line',
  data:{{
    labels:{turn_labels_js},
    datasets:[{{
      label:'대화 순도',
      data:{turn_purity_js},
      borderColor:'#8b5cf6',backgroundColor:'rgba(139,92,246,0.1)',
      borderWidth:2,fill:true,tension:0.4,pointBackgroundColor:'#8b5cf6'
    }}]
  }},
  options:{{
    responsive:true,
    scales:{{
      y:{{min:0,max:100,ticks:{{color:'#94a3b8'}},grid:{{color:'#334155'}}}},
      x:{{ticks:{{color:'#94a3b8'}},grid:{{color:'#334155'}}}}
    }},
    plugins:{{legend:{{display:false}}}}
  }}
}});
</script>
</body>
</html>"""


# ── 진입점 ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="vibe",
        description="VibeGraph - 바이브코딩 대화 순도 분석 CLI",
    )
    sub = parser.add_subparsers(dest="cmd")

    ps = sub.add_parser("start", help="작업 시작")
    ps.add_argument("project", help="프로젝트명")
    ps.add_argument("task", nargs="+", help="작업명 (공백 포함 가능)")

    sub.add_parser("prompt", help="채점 프롬프트 복사 + result.json 열기")

    pe = sub.add_parser("end", help="작업 종료 및 리포트 생성")
    pe.add_argument("--file", help="결과 JSON 경로 (기본: 세션폴더/result.json)")

    pl = sub.add_parser("list", help="세션 목록")
    pl.add_argument("project", nargs="?", help="특정 프로젝트만 조회")

    pst = sub.add_parser("stats", help="기간별 통계")
    pst.add_argument("--weeks", type=int, default=3, help="조회 주수 (기본:3)")

    pd = sub.add_parser("dashboard", aliases=["view", "index"],
                        help="전체 작업 조회 페이지(index.html) 생성/열기")
    pd.add_argument("--no-open", action="store_true", help="생성만 하고 브라우저로 열지 않음")

    pg = sub.add_parser("growth",
                        help=f"성장 리포트(growth.html) 생성/열기 (기본: 최근 {DEFAULT_GROWTH_WEEKS}주)")
    pg.add_argument("--project", help="특정 프로젝트만 분석")
    pg.add_argument("--weeks", type=int, help="최근 N주만 분석")
    pg.add_argument("--all", action="store_true", help="전체 기간 분석(기본 기간 제한 해제)")
    pg.add_argument("--no-open", action="store_true", help="생성만 하고 브라우저로 열지 않음")

    sub.add_parser("coach", help="누적 신호 기반 코칭 프롬프트 복사")

    ROOT.mkdir(parents=True, exist_ok=True)

    args = parser.parse_args()
    if args.cmd == "start":
        cmd_start(args)
    elif args.cmd == "prompt":
        cmd_prompt(args)
    elif args.cmd == "end":
        cmd_end(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "stats":
        cmd_stats(args)
    elif args.cmd in ("dashboard", "view", "index"):
        cmd_dashboard(args)
    elif args.cmd == "growth":
        cmd_growth(args)
    elif args.cmd == "coach":
        cmd_coach(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
