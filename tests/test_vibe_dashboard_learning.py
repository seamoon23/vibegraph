import unittest

import vibe


class DashboardLearningTests(unittest.TestCase):
    def test_dashboard_html_includes_domain_learning_summary(self):
        html = vibe.generate_index_html(
            [
                {
                    "project": "demo",
                    "task": "Docker task",
                    "date": "20260628",
                    "time": "0301",
                    "total": 72,
                    "grade": "B",
                    "turn_count": 5,
                    "est_tokens": 1000,
                    "report": "demo/20260628_0301_task/report.html",
                    "criteria": {
                        "one_shot": 18,
                        "context_drift": 18,
                        "ai_control": 18,
                        "prompt_clarity": 18,
                    },
                    "smells": ["Vague Instruction"],
                    "top_improvement": "Name environment assumptions early.",
                }
            ],
            learning={
                "total": 3,
                "open": 2,
                "high_open": 1,
                "by_domain": {"Docker": 2, "Oracle": 1},
                "review_candidates": [
                    {
                        "id": "LC-20260628-docker-logs",
                        "domain": "Docker",
                        "type": "tool_gap",
                        "title": "Docker container log triage",
                        "severity": 4,
                        "status": "open",
                    }
                ],
            },
        )

        self.assertIn("Domain Learning", html)
        self.assertIn("열린 Learning Card", html)
        self.assertIn("LC-20260628-docker-logs", html)
        self.assertIn("vibe learn show LC-20260628-docker-logs", html)
        self.assertIn("vibe learn archive LC-20260628-docker-logs", html)
        self.assertIn("vibe learn list --status archived", html)
        self.assertIn("Docker container log triage", html)
        self.assertIn('id="summary"', html)
        self.assertIn('id="ai-review"', html)
        self.assertIn('id="domain-learning"', html)
        self.assertIn('id="sessions"', html)
        self.assertIn('id="settings"', html)
        self.assertIn('id="q"', html)
        self.assertIn('id="pf"', html)
        self.assertIn('id="tbl"', html)
        self.assertIn("var rowsAll=", html)
        self.assertIn("th[data-sort]", html)
        self.assertIn('data-search="demo docker task"', html)
        self.assertIn('data-total="72"', html)
        self.assertIn('data-date="202606280301"', html)
        self.assertIn("Name environment assumptions early.", html)


if __name__ == "__main__":
    unittest.main()
