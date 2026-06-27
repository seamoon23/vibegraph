import json
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


if __name__ == "__main__":
    unittest.main()
