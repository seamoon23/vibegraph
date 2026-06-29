import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import vibe_learning


class LearningLayerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.task_dir = self.root / "demo" / "20260628_0101_task"
        self.task_dir.mkdir(parents=True)
        self.session = {
            "project": "demo",
            "task": "Fix invalid Oracle object",
            "started_at": "2026-06-28T01:01:00",
            "task_dir": str(self.task_dir),
        }
        self.result = {
            "scores": {
                "one_shot": 20,
                "context_drift": 18,
                "ai_control": 19,
                "prompt_clarity": 17,
                "total": 74,
            },
            "grade": "B",
            "turn_count": 8,
            "est_tokens": 12000,
            "domain_learning": {
                "session_learning_summary": "Oracle invalid object diagnosis was unclear.",
                "learning_signals": [
                    {
                        "id": "LC-20260628-oracle-invalid-object",
                        "domain": "Oracle",
                        "type": "concept_gap",
                        "title": "INVALID object diagnosis order",
                        "evidence": "Needed a clearer order for owner, grant, synonym checks.",
                        "severity": 4,
                        "recurrence": 1,
                        "confidence": "medium",
                        "micro_summary": "Invalid objects can come from referenced objects or grants.",
                        "micro_goal": "Explain first-pass INVALID object checks in five minutes.",
                        "self_checkpoints": [
                            "Check referenced object owner.",
                            "Check direct grant versus role grant.",
                        ],
                        "references": [
                            {
                                "title": "Oracle invalid objects",
                                "url": "https://docs.oracle.com/",
                                "type": "official_doc",
                                "note": "Official docs candidate.",
                            }
                        ],
                    }
                ],
            },
        }

    def tearDown(self):
        self.tmp.cleanup()

    def test_extract_learning_signals_returns_empty_list_for_legacy_json(self):
        self.assertEqual(vibe_learning.extract_learning_signals({"scores": {}}), [])

    def test_ingest_learning_result_saves_card_reference_and_session_markdown(self):
        cards = vibe_learning.ingest_learning_result(
            self.root,
            self.session,
            self.result,
            self.task_dir,
            result_json_path=self.task_dir / "result.json",
            data_json_path=self.task_dir / "data.json",
            report_path=self.task_dir / "report.html",
        )

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]["id"], "LC-20260628-oracle-invalid-object")
        self.assertTrue((self.root / "ai_sessions.db").exists())
        self.assertTrue((self.root / "learnings.db").exists())

        stored = vibe_learning.list_learning_cards(self.root)
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["domain"], "Oracle")
        self.assertEqual(stored[0]["type"], "concept_gap")
        self.assertEqual(stored[0]["status"], "open")

        refs = vibe_learning.list_learning_references(self.root, stored[0]["id"])
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0]["url"], "https://docs.oracle.com/")

        session_card = self.task_dir / "learning_card.md"
        self.assertTrue(session_card.exists())
        text = session_card.read_text(encoding="utf-8")
        self.assertIn("INVALID object diagnosis order", text)
        self.assertIn("Check referenced object owner.", text)

    def test_export_learnings_generated_markdown_preserves_manual_file(self):
        vibe_learning.ingest_learning_result(self.root, self.session, self.result, self.task_dir)
        manual = self.root / "LEARNINGS.md"
        manual.write_text("# Manual notes\n", encoding="utf-8")

        export_path = vibe_learning.export_learnings_markdown(self.root)

        self.assertEqual(export_path.name, "LEARNINGS.generated.md")
        self.assertEqual(manual.read_text(encoding="utf-8"), "# Manual notes\n")
        text = export_path.read_text(encoding="utf-8")
        self.assertIn("Learning Backlog", text)
        self.assertIn("LC-20260628-oracle-invalid-object", text)

    def test_ingest_does_not_duplicate_existing_card_id(self):
        vibe_learning.ingest_learning_result(self.root, self.session, self.result, self.task_dir)
        vibe_learning.ingest_learning_result(self.root, self.session, self.result, self.task_dir)

        stored = vibe_learning.list_learning_cards(self.root)
        self.assertEqual([card["id"] for card in stored], ["LC-20260628-oracle-invalid-object"])

    def test_update_card_status_and_add_reference(self):
        vibe_learning.ingest_learning_result(self.root, self.session, self.result, self.task_dir)

        updated = vibe_learning.update_learning_card_status(
            self.root,
            "LC-20260628-oracle-invalid-object",
            "done",
        )
        self.assertEqual(updated["status"], "done")
        self.assertEqual(vibe_learning.list_learning_cards(self.root, status="open"), [])
        self.assertEqual(vibe_learning.get_learning_card(self.root, updated["id"])["status"], "done")

        archived = vibe_learning.update_learning_card_status(
            self.root,
            "LC-20260628-oracle-invalid-object",
            "archived",
        )
        self.assertEqual(archived["status"], "archived")
        self.assertEqual(vibe_learning.list_learning_cards(self.root, status="archived")[0]["id"], archived["id"])
        with self.assertRaises(ValueError):
            vibe_learning.update_learning_card_status(self.root, archived["id"], "deleted")

        ref = vibe_learning.add_learning_reference(
            self.root,
            updated["id"],
            title="Internal runbook",
            url="file://team/oracle-invalid-object.md",
            ref_type="internal_doc",
            note="Team checklist candidate.",
        )
        self.assertEqual(ref["url"], "file://team/oracle-invalid-object.md")
        refs = vibe_learning.list_learning_references(self.root, updated["id"])
        self.assertEqual(refs[-1]["title"], "Internal runbook")

        scheduled = vibe_learning.update_learning_card_review_date(
            self.root,
            updated["id"],
            "2026-07-01",
        )
        self.assertEqual(scheduled["next_review_at"], "2026-07-01")
        with self.assertRaises(ValueError):
            vibe_learning.update_learning_card_review_date(self.root, updated["id"], "2026/07/01")

    def test_manual_card_creation_and_filtered_listing(self):
        vibe_learning.ingest_learning_result(self.root, self.session, self.result, self.task_dir)
        manual = vibe_learning.create_manual_learning_card(
            self.root,
            domain="Docker",
            signal_type="tool_gap",
            title="Docker log triage checklist",
            evidence="Manual note from production support.",
            severity=5,
            confidence="high",
            micro_summary="Check status, logs, and restart count first.",
            micro_goal="Explain Docker log triage in five minutes.",
            self_checkpoints=["Run docker ps -a.", "Check restart count."],
        )

        self.assertTrue(manual["id"].startswith("LC-"))
        docker_cards = vibe_learning.list_learning_cards(
            self.root,
            domain="Docker",
            signal_type="tool_gap",
            min_severity=5,
            search="triage",
        )
        self.assertEqual([card["id"] for card in docker_cards], [manual["id"]])
        self.assertEqual(vibe_learning.list_learning_cards(self.root, domain="Oracle")[0]["domain"], "Oracle")

    def test_learning_card_sort_modes_keep_default_available(self):
        vibe_learning.ingest_learning_result(self.root, self.session, self.result, self.task_dir)
        docker = vibe_learning.create_manual_learning_card(
            self.root,
            domain="Docker",
            signal_type="tool_gap",
            title="Docker log triage checklist",
            severity=5,
        )
        css = vibe_learning.create_manual_learning_card(
            self.root,
            domain="CSS",
            signal_type="concept_gap",
            title="CSS cascade refresher",
            severity=2,
        )

        by_severity = vibe_learning.list_learning_cards(self.root, status=None, sort_mode="severity")
        self.assertEqual(by_severity[0]["id"], docker["id"])
        self.assertEqual(by_severity[-1]["id"], css["id"])

        by_domain = vibe_learning.list_learning_cards(self.root, status=None, sort_mode="domain")
        self.assertEqual([card["domain"] for card in by_domain], ["CSS", "Docker", "Oracle"])
        self.assertEqual(
            [card["id"] for card in vibe_learning.list_learning_cards(self.root, status=None)],
            [card["id"] for card in vibe_learning.list_learning_cards(self.root, status=None, sort_mode="created")],
        )

        with self.assertRaises(ValueError):
            vibe_learning.list_learning_cards(self.root, status=None, sort_mode="random")

    def test_learning_card_due_filter_uses_next_review_date(self):
        due_result = json.loads(json.dumps(self.result))
        due_result["domain_learning"]["learning_signals"] = [
            {
                "id": "LC-20260628-due-open",
                "domain": "Docker",
                "type": "tool_gap",
                "title": "Due open card",
                "severity": 4,
                "next_review_at": "2026-06-28T09:00:00",
            },
            {
                "id": "LC-20260628-future-open",
                "domain": "Oracle",
                "type": "concept_gap",
                "title": "Future open card",
                "severity": 5,
                "next_review_at": "2026-06-29",
            },
            {
                "id": "LC-20260628-no-date",
                "domain": "CSS",
                "type": "concept_gap",
                "title": "No review date",
                "severity": 3,
            },
            {
                "id": "LC-20260628-due-done",
                "domain": "Git",
                "type": "tool_gap",
                "title": "Due done card",
                "severity": 2,
                "status": "done",
                "next_review_at": "2026-06-27",
            },
        ]
        vibe_learning.ingest_learning_result(self.root, self.session, due_result, self.task_dir)

        due_open = vibe_learning.list_learning_cards(self.root, status="open", due=True, as_of="2026-06-28")
        self.assertEqual([card["id"] for card in due_open], ["LC-20260628-due-open"])

        due_all = vibe_learning.list_learning_cards(self.root, status=None, due=True, as_of="2026-06-28")
        self.assertEqual([card["id"] for card in due_all], ["LC-20260628-due-done", "LC-20260628-due-open"])

    def test_get_next_learning_card_prefers_due_then_high_severity_open_card(self):
        next_result = json.loads(json.dumps(self.result))
        next_result["domain_learning"]["learning_signals"] = [
            {
                "id": "LC-20260628-low-due",
                "domain": "Docker",
                "type": "tool_gap",
                "title": "Low due card",
                "severity": 2,
                "next_review_at": "2026-06-28",
            },
            {
                "id": "LC-20260628-high-future",
                "domain": "Oracle",
                "type": "concept_gap",
                "title": "High future card",
                "severity": 5,
                "next_review_at": "2026-07-02",
            },
            {
                "id": "LC-20260628-mid-open",
                "domain": "Spring",
                "type": "concept_gap",
                "title": "Mid open card",
                "severity": 4,
            },
        ]
        vibe_learning.ingest_learning_result(self.root, self.session, next_result, self.task_dir)

        due_next = vibe_learning.get_next_learning_card(self.root, as_of="2026-06-28")
        self.assertEqual(due_next["id"], "LC-20260628-low-due")

        fallback_next = vibe_learning.get_next_learning_card(self.root, as_of="2026-06-27")
        self.assertEqual(fallback_next["id"], "LC-20260628-high-future")

    def test_learning_summary_review_candidates_follow_next_card_priority(self):
        summary_result = json.loads(json.dumps(self.result))
        summary_result["domain_learning"]["learning_signals"] = [
            {
                "id": "LC-20260628-low-due",
                "domain": "Docker",
                "type": "tool_gap",
                "title": "Low due card",
                "severity": 2,
                "next_review_at": "2026-06-28",
            },
            {
                "id": "LC-20260628-high-future",
                "domain": "Oracle",
                "type": "concept_gap",
                "title": "High future card",
                "severity": 5,
                "next_review_at": "2026-07-02",
            },
        ]
        vibe_learning.ingest_learning_result(self.root, self.session, summary_result, self.task_dir)

        summary = vibe_learning.learning_summary(self.root, as_of="2026-06-28")

        self.assertEqual(
            [card["id"] for card in summary["review_candidates"]],
            ["LC-20260628-low-due", "LC-20260628-high-future"],
        )

    def test_init_learnings_db_adds_next_review_column_to_legacy_db(self):
        db_path = vibe_learning.learnings_db_path(self.root)
        with sqlite3.connect(db_path) as con:
            con.execute(
                """
                CREATE TABLE learning_cards (
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
                    raw_json TEXT
                )
                """
            )
            con.execute(
                """
                CREATE TABLE learning_references (
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
            con.execute(
                """
                INSERT INTO learning_cards (
                    id, source_session_id, source_project, source_task,
                    created_at, updated_at, domain, type, title, evidence,
                    severity, recurrence, confidence, micro_summary,
                    micro_goal, status, raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "LC-legacy-card",
                    "legacy-session",
                    "LegacyProject",
                    "Legacy task",
                    "2026-06-01T09:00:00",
                    "2026-06-01T09:00:00",
                    "Docker",
                    "tool_gap",
                    "Legacy Docker card",
                    "Old DB row without next_review_at.",
                    4,
                    1,
                    "medium",
                    "Legacy rows should keep working after migration.",
                    "Review migrated card.",
                    "open",
                    "{}",
                ),
            )

        vibe_learning.init_learnings_db(self.root)

        with sqlite3.connect(db_path) as con:
            columns = [row[1] for row in con.execute("PRAGMA table_info(learning_cards)").fetchall()]
        self.assertIn("next_review_at", columns)

        listed = vibe_learning.list_learning_cards(self.root)
        self.assertEqual(listed[0]["id"], "LC-legacy-card")
        self.assertEqual(listed[0]["next_review_at"], "")

        shown = vibe_learning.get_learning_card(self.root, "LC-legacy-card")
        self.assertEqual(shown["title"], "Legacy Docker card")

        scheduled = vibe_learning.update_learning_card_review_date(
            self.root,
            "LC-legacy-card",
            "2026-07-02",
        )
        self.assertEqual(scheduled["next_review_at"], "2026-07-02")


if __name__ == "__main__":
    unittest.main()
