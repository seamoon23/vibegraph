import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class VibeCliLearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = Path(__file__).resolve().parents[1]
        self.env = os.environ.copy()
        self.env["VIBE_HOME"] = str(self.root)
        self.env["PYTHONUTF8"] = "1"
        self.task_dir = self.root / "demo" / "20260628_0301_learning"
        self.task_dir.mkdir(parents=True)
        (self.root / ".current_session.json").write_text(
            json.dumps(
                {
                    "project": "demo",
                    "task": "Learning CLI integration",
                    "started_at": "2026-06-28T03:01:00",
                    "task_dir": str(self.task_dir),
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (self.task_dir / "result.json").write_text(
            json.dumps(
                {
                    "scores": {
                        "one_shot": 18,
                        "context_drift": 18,
                        "ai_control": 18,
                        "prompt_clarity": 18,
                    },
                    "grade": "B",
                    "summary": "Solid session with one domain gap.",
                    "top_improvement": "Name environment assumptions early.",
                    "domain_learning": {
                        "session_learning_summary": "Docker log diagnosis needs a shorter path.",
                        "learning_signals": [
                            {
                                "id": "LC-20260628-docker-logs",
                                "domain": "Docker",
                                "type": "tool_gap",
                                "title": "Docker container log triage",
                                "evidence": "Needed a repeatable first pass for container logs.",
                                "severity": 4,
                                "confidence": "high",
                                "micro_summary": "Start with container status, recent logs, and restart count.",
                                "micro_goal": "Explain a three-command Docker log triage path.",
                            }
                        ],
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_vibe(self, *args):
        return subprocess.run(
            [sys.executable, "vibe.py", *args],
            cwd=self.repo,
            env=self.env,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )

    def test_end_ingests_learning_and_learn_commands_read_it(self):
        end = self.run_vibe("end")
        self.assertEqual(end.returncode, 0, end.stdout + end.stderr)
        self.assertTrue((self.task_dir / "learning_card.md").exists())

        listing = self.run_vibe("learn", "list")
        self.assertEqual(listing.returncode, 0, listing.stdout + listing.stderr)
        self.assertIn("LC-20260628-docker-logs", listing.stdout)
        self.assertIn("Docker", listing.stdout)

        last = self.run_vibe("learn", "card", "--last")
        self.assertEqual(last.returncode, 0, last.stdout + last.stderr)
        self.assertIn("Docker container log triage", last.stdout)

        report = self.run_vibe("learn", "report")
        self.assertEqual(report.returncode, 0, report.stdout + report.stderr)
        self.assertIn("Severity Top 5", report.stdout)

        export = self.run_vibe("learn", "export")
        self.assertEqual(export.returncode, 0, export.stdout + export.stderr)
        self.assertTrue((self.root / "LEARNINGS.generated.md").exists())


if __name__ == "__main__":
    unittest.main()
