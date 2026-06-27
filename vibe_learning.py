#!/usr/bin/env python3
from __future__ import annotations

import datetime
import json
import re
import sqlite3
from pathlib import Path
from typing import Any


LEARNING_TYPES = {
    "concept_gap",
    "error_pattern",
    "tool_gap",
    "environment_gap",
    "domain_gap",
    "prompt_gap",
    "decision_gap",
}


def ai_sessions_db_path(root: Path) -> Path:
    return Path(root) / "ai_sessions.db"


def learnings_db_path(root: Path) -> Path:
    return Path(root) / "learnings.db"


def init_ai_sessions_db(root: Path) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    db_path = ai_sessions_db_path(root)
    with sqlite3.connect(db_path) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_sessions (
                session_id TEXT PRIMARY KEY,
                project TEXT,
                task TEXT,
                created_at TEXT,
                updated_at TEXT,
                grade TEXT,
                total_score INTEGER,
                one_shot INTEGER,
                context_drift INTEGER,
                ai_control INTEGER,
                prompt_clarity INTEGER,
                turn_count INTEGER,
                est_tokens INTEGER,
                report_path TEXT,
                result_json_path TEXT,
                data_json_path TEXT,
                raw_json TEXT
            )
            """
        )
    return db_path


def init_learnings_db(root: Path) -> Path:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    db_path = learnings_db_path(root)
    with sqlite3.connect(db_path) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_cards (
                id TEXT PRIMARY KEY,
                source_session_id TEXT,
                source_project TEXT,
                source_task TEXT,
                created_at TEXT,
                updated_at TEXT,
                domain TEXT,
                type TEXT,
                title TEXT,
                evidence TEXT,
                severity INTEGER,
                recurrence INTEGER DEFAULT 1,
                confidence TEXT,
                micro_summary TEXT,
                micro_goal TEXT,
                status TEXT DEFAULT 'open',
                next_review_at TEXT,
                raw_json TEXT
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT,
                title TEXT,
                url TEXT,
                ref_type TEXT,
                note TEXT,
                created_at TEXT
            )
            """
        )
    return db_path


def normalize_ai_review_result(raw: dict[str, Any]) -> dict[str, Any]:
    scores = dict(raw.get("scores") or {})
    total = _as_int(scores.get("total"))
    if total == 0:
        total = sum(_as_int(scores.get(k)) for k in ("one_shot", "context_drift", "ai_control", "prompt_clarity"))
    return {
        "scores": scores,
        "grade": raw.get("grade") or "",
        "total_score": total,
        "turn_count": _as_int(raw.get("turn_count")),
        "est_tokens": _as_int(raw.get("est_tokens")),
    }


def extract_learning_signals(raw: dict[str, Any]) -> list[dict[str, Any]]:
    domain_learning = raw.get("domain_learning")
    if not isinstance(domain_learning, dict):
        return []
    signals = domain_learning.get("learning_signals")
    if not isinstance(signals, list):
        return []
    return [s for s in signals if isinstance(s, dict)]


def ingest_learning_result(
    root: Path,
    session: dict[str, Any],
    result: dict[str, Any],
    task_dir: Path,
    result_json_path: Path | None = None,
    data_json_path: Path | None = None,
    report_path: Path | None = None,
) -> list[dict[str, Any]]:
    root = Path(root)
    task_dir = Path(task_dir)
    now = datetime.datetime.now().isoformat(timespec="seconds")
    session_id = _session_id(session, task_dir)

    save_ai_session(
        root,
        session,
        result,
        session_id=session_id,
        result_json_path=result_json_path,
        data_json_path=data_json_path,
        report_path=report_path,
        now=now,
    )

    signals = extract_learning_signals(result)
    if not signals:
        return []

    cards = [
        normalize_learning_signal(signal, session, result, task_dir, session_id, idx, now)
        for idx, signal in enumerate(signals, 1)
    ]
    save_learning_cards(root, cards, now=now)
    write_session_learning_card(
        task_dir,
        cards,
        summary=(result.get("domain_learning") or {}).get("session_learning_summary", ""),
    )
    return cards


def save_ai_session(
    root: Path,
    session: dict[str, Any],
    result: dict[str, Any],
    session_id: str,
    result_json_path: Path | None = None,
    data_json_path: Path | None = None,
    report_path: Path | None = None,
    now: str | None = None,
) -> None:
    init_ai_sessions_db(root)
    now = now or datetime.datetime.now().isoformat(timespec="seconds")
    norm = normalize_ai_review_result(result)
    scores = norm["scores"]
    created_at = session.get("started_at") or result.get("started_at") or now
    with sqlite3.connect(ai_sessions_db_path(root)) as con:
        con.execute(
            """
            INSERT INTO ai_sessions (
                session_id, project, task, created_at, updated_at, grade, total_score,
                one_shot, context_drift, ai_control, prompt_clarity, turn_count,
                est_tokens, report_path, result_json_path, data_json_path, raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                project=excluded.project,
                task=excluded.task,
                updated_at=excluded.updated_at,
                grade=excluded.grade,
                total_score=excluded.total_score,
                one_shot=excluded.one_shot,
                context_drift=excluded.context_drift,
                ai_control=excluded.ai_control,
                prompt_clarity=excluded.prompt_clarity,
                turn_count=excluded.turn_count,
                est_tokens=excluded.est_tokens,
                report_path=excluded.report_path,
                result_json_path=excluded.result_json_path,
                data_json_path=excluded.data_json_path,
                raw_json=excluded.raw_json
            """,
            (
                session_id,
                session.get("project", ""),
                session.get("task", ""),
                created_at,
                now,
                norm["grade"],
                norm["total_score"],
                _as_int(scores.get("one_shot")),
                _as_int(scores.get("context_drift")),
                _as_int(scores.get("ai_control")),
                _as_int(scores.get("prompt_clarity")),
                norm["turn_count"],
                norm["est_tokens"],
                _path_text(report_path),
                _path_text(result_json_path),
                _path_text(data_json_path),
                json.dumps(result, ensure_ascii=False),
            ),
        )


def normalize_learning_signal(
    signal: dict[str, Any],
    session: dict[str, Any],
    result: dict[str, Any],
    task_dir: Path,
    session_id: str,
    index: int,
    now: str,
) -> dict[str, Any]:
    created_at = result.get("ended_at") or now
    domain = str(signal.get("domain") or "Etc").strip() or "Etc"
    signal_type = str(signal.get("type") or "domain_gap").strip() or "domain_gap"
    if signal_type not in LEARNING_TYPES:
        signal_type = "domain_gap"
    title = str(signal.get("title") or "Untitled learning card").strip()
    card_id = str(signal.get("id") or "").strip() or _make_card_id(created_at, domain, title, index)
    card = {
        "id": card_id,
        "source_session_id": session_id,
        "source_project": session.get("project", ""),
        "source_task": session.get("task", ""),
        "created_at": created_at,
        "updated_at": now,
        "domain": domain,
        "type": signal_type,
        "title": title,
        "evidence": str(signal.get("evidence") or "").strip(),
        "severity": _bounded_int(signal.get("severity"), 1, 5, 3),
        "recurrence": max(1, _as_int(signal.get("recurrence"), 1)),
        "confidence": str(signal.get("confidence") or "medium").strip() or "medium",
        "micro_summary": str(signal.get("micro_summary") or "").strip(),
        "micro_goal": str(signal.get("micro_goal") or "").strip(),
        "status": str(signal.get("status") or "open").strip() or "open",
        "next_review_at": str(signal.get("next_review_at") or "").strip(),
        "raw_json": json.dumps(signal, ensure_ascii=False),
        "references": _normalize_references(signal.get("references")),
        "self_checkpoints": _string_list(signal.get("self_checkpoints")),
    }
    return card


def save_learning_cards(root: Path, cards: list[dict[str, Any]], now: str | None = None) -> None:
    init_learnings_db(root)
    now = now or datetime.datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(learnings_db_path(root)) as con:
        for card in cards:
            existing = con.execute(
                "SELECT created_at, recurrence, status FROM learning_cards WHERE id = ?",
                (card["id"],),
            ).fetchone()
            created_at = existing[0] if existing else card["created_at"]
            recurrence = max(_as_int(card.get("recurrence"), 1), _as_int(existing[1], 1) if existing else 1)
            status = existing[2] if existing and existing[2] else card.get("status", "open")
            con.execute(
                """
                INSERT OR REPLACE INTO learning_cards (
                    id, source_session_id, source_project, source_task, created_at, updated_at,
                    domain, type, title, evidence, severity, recurrence, confidence,
                    micro_summary, micro_goal, status, next_review_at, raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    card["id"],
                    card.get("source_session_id", ""),
                    card.get("source_project", ""),
                    card.get("source_task", ""),
                    created_at,
                    now,
                    card.get("domain", "Etc"),
                    card.get("type", "domain_gap"),
                    card.get("title", ""),
                    card.get("evidence", ""),
                    _as_int(card.get("severity"), 3),
                    recurrence,
                    card.get("confidence", "medium"),
                    card.get("micro_summary", ""),
                    card.get("micro_goal", ""),
                    status,
                    card.get("next_review_at", ""),
                    card.get("raw_json", "{}"),
                ),
            )
            con.execute("DELETE FROM learning_references WHERE card_id = ?", (card["id"],))
            for ref in card.get("references", []):
                con.execute(
                    """
                    INSERT INTO learning_references
                        (card_id, title, url, ref_type, note, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        card["id"],
                        ref.get("title", ""),
                        ref.get("url", ""),
                        ref.get("type", "etc"),
                        ref.get("note", ""),
                        now,
                    ),
                )


def list_learning_cards(root: Path, status: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    init_learnings_db(root)
    query = "SELECT * FROM learning_cards"
    params: list[Any] = []
    if status:
        query += " WHERE status = ?"
        params.append(status)
    query += " ORDER BY created_at DESC, severity DESC, id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    with sqlite3.connect(learnings_db_path(root)) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(query, params).fetchall()
    return [_row_to_card(row) for row in rows]


def list_learning_references(root: Path, card_id: str) -> list[dict[str, str]]:
    init_learnings_db(root)
    with sqlite3.connect(learnings_db_path(root)) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT title, url, ref_type, note
            FROM learning_references
            WHERE card_id = ?
            ORDER BY id
            """,
            (card_id,),
        ).fetchall()
    return [
        {
            "title": row["title"],
            "url": row["url"],
            "type": row["ref_type"],
            "note": row["note"],
        }
        for row in rows
    ]


def get_last_learning_card(root: Path) -> dict[str, Any] | None:
    cards = list_learning_cards(root, limit=1)
    return cards[0] if cards else None


def write_session_learning_card(task_dir: Path, cards: list[dict[str, Any]], summary: str = "") -> Path | None:
    if not cards:
        return None
    task_dir = Path(task_dir)
    task_dir.mkdir(parents=True, exist_ok=True)
    out = task_dir / "learning_card.md"
    parts = ["# Learning Cards\n"]
    if summary:
        parts.append(f"> {summary}\n")
    for card in cards:
        parts.append(render_learning_card_md(card))
    out.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    return out


def render_learning_card_md(card: dict[str, Any], references: list[dict[str, str]] | None = None) -> str:
    references = references if references is not None else card.get("references", [])
    checkpoints = card.get("self_checkpoints")
    if not checkpoints:
        try:
            raw = json.loads(card.get("raw_json") or "{}")
            checkpoints = _string_list(raw.get("self_checkpoints"))
        except Exception:
            checkpoints = []

    lines = [
        f"### {card.get('id', '')}. {card.get('title', '')}",
        "",
        "```yaml",
        f"id: {card.get('id', '')}",
        f"date: {str(card.get('created_at', ''))[:10]}",
        f"domain: {card.get('domain', 'Etc')}",
        f"type: {card.get('type', 'domain_gap')}",
        f"severity: {card.get('severity', 3)}",
        f"recurrence: {card.get('recurrence', 1)}",
        f"confidence: {card.get('confidence', 'medium')}",
        f"status: {card.get('status', 'open')}",
        f"source_session_id: {card.get('source_session_id', '')}",
        "```",
        "",
        "핵심 개념 1줄 요약",
        f"- {card.get('micro_summary') or card.get('evidence') or '요약 없음'}",
        "",
        "5분 복습 목표",
        f"- {card.get('micro_goal') or '다음 작업 전에 이 주제를 5분 안에 설명한다.'}",
        "",
        "다음 작업 시 셀프 체크포인트",
    ]
    if checkpoints:
        lines.extend(f"- [ ] {item}" for item in checkpoints)
    else:
        lines.append("- [ ] 같은 상황에서 원인 확인 순서를 말할 수 있는가?")
    lines.extend(["", "참고 링크"])
    if references:
        for ref in references:
            label = ref.get("title") or ref.get("url") or "reference"
            note = f" - {ref.get('note')}" if ref.get("note") else ""
            lines.append(f"- [{label}]({ref.get('url')}){note}")
    else:
        lines.append("- 없음")
    return "\n".join(lines)


def export_learnings_markdown(root: Path) -> Path:
    init_learnings_db(root)
    cards = list_learning_cards(root, status=None)
    out = Path(root) / "LEARNINGS.generated.md"
    rows = []
    body = []
    for card in cards:
        date = str(card.get("created_at", ""))[:10]
        rows.append(
            "| {id} | {date} | {domain} | {type} | {title} | {severity} | {recurrence} | {status} |".format(
                id=card.get("id", ""),
                date=date,
                domain=card.get("domain", ""),
                type=card.get("type", ""),
                title=str(card.get("title", "")).replace("|", "/"),
                severity=card.get("severity", ""),
                recurrence=card.get("recurrence", ""),
                status=card.get("status", ""),
            )
        )
        body.append(render_learning_card_md(card, list_learning_references(root, card["id"])))

    text = "\n".join(
        [
            "# LEARNINGS.md",
            "",
            "> AI 작업 이후 드러난 개발/DB/인프라/업무도메인 지식 공백을 5~10분 단위로 누적 관리한다.",
            "",
            "## Learning Backlog",
            "",
            "| ID | 날짜 | 도메인 | 타입 | 제목 | 우선순위 | 반복 | 상태 |",
            "|---|---:|---|---|---|---:|---:|---|",
            *rows,
            "",
            "## Active Learning Cards",
            "",
            "\n\n".join(body) if body else "아직 Learning Card가 없습니다.",
            "",
            "## Error Playbook",
            "",
            "## Weekly Learning Report",
            "",
            "## Archive",
            "",
        ]
    )
    out.write_text(text, encoding="utf-8")
    return out


def render_learning_report(root: Path) -> str:
    cards = list_learning_cards(root, status=None)
    if not cards:
        return "아직 Learning Card가 없습니다."

    by_domain: dict[str, int] = {}
    by_status: dict[str, int] = {}
    repeated = []
    for card in cards:
        by_domain[card["domain"]] = by_domain.get(card["domain"], 0) + 1
        by_status[card["status"]] = by_status.get(card["status"], 0) + 1
        if _as_int(card.get("recurrence")) > 1:
            repeated.append(card)
    high = sorted(cards, key=lambda c: (_as_int(c.get("severity")), c.get("created_at", "")), reverse=True)[:5]
    review = [c for c in high if c.get("status") == "open"][:5]

    lines = ["Learning Report", ""]
    lines.append("[도메인별 카드 수]")
    lines.extend(f"- {domain}: {count}" for domain, count in sorted(by_domain.items()))
    lines.append("")
    lines.append("[상태별 카드 수]")
    lines.extend(f"- {status}: {count}" for status, count in sorted(by_status.items()))
    lines.append("")
    lines.append("[Severity Top 5]")
    lines.extend(f"- {card['id']} ({card['severity']}): {card['title']}" for card in high)
    lines.append("")
    lines.append("[반복 발생 항목]")
    if repeated:
        lines.extend(f"- {card['id']} x{card['recurrence']}: {card['title']}" for card in repeated)
    else:
        lines.append("- 없음")
    lines.append("")
    lines.append("[이번 주 5분 복습 후보]")
    lines.extend(f"- {card['id']}: {card['micro_goal'] or card['title']}" for card in review)
    return "\n".join(lines)


def learning_summary(root: Path) -> dict[str, Any]:
    if not learnings_db_path(root).exists():
        return {
            "total": 0,
            "open": 0,
            "high_open": 0,
            "by_domain": {},
            "review_candidates": [],
        }
    cards = list_learning_cards(root, status=None)
    open_cards = [c for c in cards if c.get("status") == "open"]
    high_open = [c for c in open_cards if _as_int(c.get("severity")) >= 4]
    by_domain: dict[str, int] = {}
    for card in cards:
        by_domain[card["domain"]] = by_domain.get(card["domain"], 0) + 1
    return {
        "total": len(cards),
        "open": len(open_cards),
        "high_open": len(high_open),
        "by_domain": by_domain,
        "review_candidates": sorted(
            open_cards,
            key=lambda c: (_as_int(c.get("severity")), c.get("created_at", "")),
            reverse=True,
        )[:5],
    }


def _row_to_card(row: sqlite3.Row) -> dict[str, Any]:
    card = dict(row)
    try:
        raw = json.loads(card.get("raw_json") or "{}")
    except Exception:
        raw = {}
    card["self_checkpoints"] = _string_list(raw.get("self_checkpoints"))
    return card


def _normalize_references(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    refs = []
    for item in value:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        refs.append(
            {
                "title": str(item.get("title") or url).strip(),
                "url": url,
                "type": str(item.get("type") or item.get("ref_type") or "etc").strip(),
                "note": str(item.get("note") or "").strip(),
            }
        )
    return refs


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _make_card_id(created_at: str, domain: str, title: str, index: int) -> str:
    date = re.sub(r"[^0-9]", "", created_at[:10]) or datetime.datetime.now().strftime("%Y%m%d")
    slug_src = f"{domain}-{title}".lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug_src).strip("-") or "learning"
    slug = slug[:42].strip("-")
    return f"LC-{date}-{slug}-{index:03d}"


def _session_id(session: dict[str, Any], task_dir: Path) -> str:
    if session.get("session_id"):
        return str(session["session_id"])
    name = Path(task_dir).name
    project = str(session.get("project") or Path(task_dir).parent.name or "unknown")
    return f"{project}/{name}"


def _bounded_int(value: Any, minimum: int, maximum: int, default: int) -> int:
    return max(minimum, min(maximum, _as_int(value, default)))


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _path_text(path: Path | None) -> str:
    return str(path) if path else ""
