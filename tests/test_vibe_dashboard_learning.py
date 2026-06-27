import unittest

import vibe


class DashboardLearningTests(unittest.TestCase):
    def test_dashboard_html_includes_domain_learning_summary(self):
        html = vibe.generate_index_html(
            [],
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
        self.assertIn("Docker container log triage", html)


if __name__ == "__main__":
    unittest.main()
