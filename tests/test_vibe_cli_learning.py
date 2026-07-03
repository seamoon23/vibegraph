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
                                "self_checkpoints": ["Which Docker command shows recent logs first?"],
                                "next_review_at": "2026-06-28",
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

        done = self.run_vibe("learn", "done", "LC-20260628-docker-logs")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.assertIn("done", done.stdout)

        open_listing = self.run_vibe("learn", "list")
        self.assertEqual(open_listing.returncode, 0, open_listing.stdout + open_listing.stderr)
        self.assertIn("아직 Learning Card가 없습니다", open_listing.stdout)

        all_listing = self.run_vibe("learn", "list", "--all")
        self.assertEqual(all_listing.returncode, 0, all_listing.stdout + all_listing.stderr)
        self.assertIn("LC-20260628-docker-logs", all_listing.stdout)
        self.assertIn("done", all_listing.stdout)

        reopened = self.run_vibe("learn", "reopen", "LC-20260628-docker-logs")
        self.assertEqual(reopened.returncode, 0, reopened.stdout + reopened.stderr)
        self.assertIn("open", reopened.stdout)

        archived = self.run_vibe("learn", "archive", "LC-20260628-docker-logs")
        self.assertEqual(archived.returncode, 0, archived.stdout + archived.stderr)
        self.assertIn("archived", archived.stdout)

        archived_listing = self.run_vibe("learn", "list", "--status", "archived")
        self.assertEqual(archived_listing.returncode, 0, archived_listing.stdout + archived_listing.stderr)
        self.assertIn("LC-20260628-docker-logs", archived_listing.stdout)
        self.assertIn("archived", archived_listing.stdout)

        archived_json = self.run_vibe("learn", "list", "--status", "archived", "--json")
        self.assertEqual(archived_json.returncode, 0, archived_json.stdout + archived_json.stderr)
        archived_payload = json.loads(archived_json.stdout)
        self.assertEqual([card["status"] for card in archived_payload], ["archived"])
        self.assertNotIn("Learning Card", archived_json.stdout)

        invalid_status = self.run_vibe("learn", "list", "--status", "deleted")
        self.assertNotEqual(invalid_status.returncode, 0)
        self.assertIn("invalid choice", invalid_status.stderr)

        invalid_filter_severity = self.run_vibe("learn", "list", "--severity", "0")
        self.assertNotEqual(invalid_filter_severity.returncode, 0)
        self.assertIn("1-5", invalid_filter_severity.stderr)

        reopened = self.run_vibe("learn", "reopen", "LC-20260628-docker-logs")
        self.assertEqual(reopened.returncode, 0, reopened.stdout + reopened.stderr)
        self.assertIn("open", reopened.stdout)

        due = self.run_vibe("learn", "list", "--due")
        self.assertEqual(due.returncode, 0, due.stdout + due.stderr)
        self.assertIn("LC-20260628-docker-logs", due.stdout)
        self.assertIn("next_review_at", due.stdout)
        self.assertIn("2026-06-28", due.stdout)

        due_json = self.run_vibe("learn", "list", "--due", "--json")
        self.assertEqual(due_json.returncode, 0, due_json.stdout + due_json.stderr)
        due_payload = json.loads(due_json.stdout)
        self.assertEqual([card["id"] for card in due_payload], ["LC-20260628-docker-logs"])
        self.assertEqual(due_payload[0]["next_review_at"], "2026-06-28")
        self.assertNotIn("next_review_at=", due_json.stdout)

        due_before_review = self.run_vibe("learn", "list", "--due", "--as-of", "2026-06-27", "--json")
        self.assertEqual(due_before_review.returncode, 0, due_before_review.stdout + due_before_review.stderr)
        self.assertEqual(json.loads(due_before_review.stdout), [])

        invalid_due_as_of = self.run_vibe("learn", "list", "--due", "--as-of", "2026/06/27")
        self.assertNotEqual(invalid_due_as_of.returncode, 0)
        self.assertIn("YYYY-MM-DD", invalid_due_as_of.stderr)

        next_card = self.run_vibe("learn", "next")
        self.assertEqual(next_card.returncode, 0, next_card.stdout + next_card.stderr)
        self.assertIn("LC-20260628-docker-logs", next_card.stdout)
        self.assertIn("Docker container log triage", next_card.stdout)

        next_json = self.run_vibe("learn", "next", "--json")
        self.assertEqual(next_json.returncode, 0, next_json.stdout + next_json.stderr)
        next_payload = json.loads(next_json.stdout)
        self.assertEqual(next_payload["id"], "LC-20260628-docker-logs")
        self.assertEqual(next_payload["next_review_at"], "2026-06-28")

        quiz = self.run_vibe("learn", "quiz", "--limit", "1")
        self.assertEqual(quiz.returncode, 0, quiz.stdout + quiz.stderr)
        self.assertIn("Learning Quiz", quiz.stdout)
        self.assertIn("Which Docker command shows recent logs first?", quiz.stdout)
        self.assertIn("Explain a three-command Docker log triage path.", quiz.stdout)
        self.assertIn("vibe learn show LC-20260628-docker-logs", quiz.stdout)

        quiz_json = self.run_vibe("learn", "quiz", "--limit", "1", "--json")
        self.assertEqual(quiz_json.returncode, 0, quiz_json.stdout + quiz_json.stderr)
        quiz_payload = json.loads(quiz_json.stdout)
        self.assertEqual(quiz_payload[0]["id"], "LC-20260628-docker-logs")
        self.assertEqual(quiz_payload[0]["questions"], ["Which Docker command shows recent logs first?"])

        scheduled = self.run_vibe("learn", "schedule", "LC-20260628-docker-logs", "--date", "2026-07-01")
        self.assertEqual(scheduled.returncode, 0, scheduled.stdout + scheduled.stderr)
        self.assertIn("2026-07-01", scheduled.stdout)

        scheduled_show = self.run_vibe("learn", "show", "LC-20260628-docker-logs", "--json")
        self.assertEqual(scheduled_show.returncode, 0, scheduled_show.stdout + scheduled_show.stderr)
        self.assertEqual(json.loads(scheduled_show.stdout)["next_review_at"], "2026-07-01")

        invalid_schedule = self.run_vibe("learn", "schedule", "LC-20260628-docker-logs", "--date", "2026/07/01")
        self.assertNotEqual(invalid_schedule.returncode, 0)

        add_ref = self.run_vibe(
            "learn",
            "add-reference",
            "LC-20260628-docker-logs",
            "--title",
            "Docker logs doc",
            "--url",
            "https://docs.docker.com/",
            "--type",
            "official_doc",
            "--note",
            "Official docs entry point.",
        )
        self.assertEqual(add_ref.returncode, 0, add_ref.stdout + add_ref.stderr)
        self.assertIn("Docker logs doc", add_ref.stdout)

        shown = self.run_vibe("learn", "show", "LC-20260628-docker-logs")
        self.assertEqual(shown.returncode, 0, shown.stdout + shown.stderr)
        self.assertIn("Docker logs doc", shown.stdout)
        self.assertIn("https://docs.docker.com/", shown.stdout)

        shown_json = self.run_vibe("learn", "show", "LC-20260628-docker-logs", "--json")
        self.assertEqual(shown_json.returncode, 0, shown_json.stdout + shown_json.stderr)
        shown_payload = json.loads(shown_json.stdout)
        self.assertEqual(shown_payload["id"], "LC-20260628-docker-logs")
        self.assertEqual(shown_payload["references"][0]["url"], "https://docs.docker.com/")

        manual = self.run_vibe(
            "learn",
            "add",
            "--domain",
            "Oracle",
            "--type",
            "concept_gap",
            "--title",
            "Oracle grants checklist",
            "--evidence",
            "Manual follow-up note.",
            "--severity",
            "5",
            "--summary",
            "Check direct grants before role grants.",
            "--goal",
            "Explain Oracle direct grants in five minutes.",
            "--checkpoint",
            "Check object owner.",
            "--checkpoint",
            "Check direct grant.",
        )
        self.assertEqual(manual.returncode, 0, manual.stdout + manual.stderr)
        self.assertIn("Oracle grants checklist", manual.stdout)

        invalid_add_severity = self.run_vibe(
            "learn",
            "add",
            "--domain",
            "Oracle",
            "--type",
            "concept_gap",
            "--title",
            "Bad severity",
            "--severity",
            "6",
        )
        self.assertNotEqual(invalid_add_severity.returncode, 0)
        self.assertIn("1-5", invalid_add_severity.stderr)

        next_as_of = self.run_vibe("learn", "next", "--as-of", "2026-06-30", "--json")
        self.assertEqual(next_as_of.returncode, 0, next_as_of.stdout + next_as_of.stderr)
        next_as_of_payload = json.loads(next_as_of.stdout)
        self.assertEqual(next_as_of_payload["domain"], "Oracle")
        self.assertEqual(next_as_of_payload["severity"], 5)

        invalid_next_as_of = self.run_vibe("learn", "next", "--as-of", "2026/06/30")
        self.assertNotEqual(invalid_next_as_of.returncode, 0)
        self.assertIn("YYYY-MM-DD", invalid_next_as_of.stderr)

        filtered = self.run_vibe(
            "learn",
            "list",
            "--all",
            "--domain",
            "Oracle",
            "--type",
            "concept_gap",
            "--severity",
            "5",
            "--search",
            "grants",
        )
        self.assertEqual(filtered.returncode, 0, filtered.stdout + filtered.stderr)
        self.assertIn("Oracle grants checklist", filtered.stdout)
        self.assertNotIn("LC-20260628-docker-logs", filtered.stdout)

        limited = self.run_vibe("learn", "list", "--all", "--limit", "1")
        self.assertEqual(limited.returncode, 0, limited.stdout + limited.stderr)
        listed_cards = [line for line in limited.stdout.splitlines() if line.strip().startswith("LC-")]
        self.assertEqual(len(listed_cards), 1)

        invalid_limit = self.run_vibe("learn", "list", "--limit", "0")
        self.assertNotEqual(invalid_limit.returncode, 0)
        self.assertIn("positive integer", invalid_limit.stderr)

        listed_json = self.run_vibe("learn", "list", "--all", "--limit", "1", "--json")
        self.assertEqual(listed_json.returncode, 0, listed_json.stdout + listed_json.stderr)
        listed_payload = json.loads(listed_json.stdout)
        self.assertEqual(len(listed_payload), 1)
        self.assertIn("id", listed_payload[0])
        self.assertNotIn("접근 경로", listed_json.stdout)

        severity_json = self.run_vibe("learn", "list", "--all", "--sort", "severity", "--json")
        self.assertEqual(severity_json.returncode, 0, severity_json.stdout + severity_json.stderr)
        severity_payload = json.loads(severity_json.stdout)
        self.assertEqual(severity_payload[0]["severity"], 5)
        self.assertEqual(severity_payload[0]["domain"], "Oracle")
        self.assertTrue(severity_json.stdout.lstrip().startswith("["))
        self.assertNotIn("Access path", severity_json.stdout)

        sorted_by_domain = self.run_vibe("learn", "list", "--all", "--sort", "domain")
        self.assertEqual(sorted_by_domain.returncode, 0, sorted_by_domain.stdout + sorted_by_domain.stderr)
        sorted_cards = [line for line in sorted_by_domain.stdout.splitlines() if line.strip().startswith("LC-")]
        self.assertIn("Docker", sorted_cards[0])
        self.assertIn("Oracle", sorted_cards[-1])

        stats = self.run_vibe("learn", "stats")
        self.assertEqual(stats.returncode, 0, stats.stdout + stats.stderr)
        self.assertIn("Learning Stats", stats.stdout)
        self.assertIn("total:", stats.stdout)
        self.assertIn("open:", stats.stdout)
        self.assertIn("archived:", stats.stdout)

        stats_json = self.run_vibe("learn", "stats", "--json")
        self.assertEqual(stats_json.returncode, 0, stats_json.stdout + stats_json.stderr)
        stats_payload = json.loads(stats_json.stdout)
        self.assertIn("total", stats_payload)
        self.assertIn("domains", stats_payload)
        self.assertNotIn("Learning Stats", stats_json.stdout)


if __name__ == "__main__":
    unittest.main()
