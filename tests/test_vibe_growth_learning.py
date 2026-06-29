import unittest

import vibe


class GrowthLearningTests(unittest.TestCase):
    def test_growth_html_includes_learning_summary_when_provided(self):
        sig = {
            "n": 1,
            "overall": 72.0,
            "ordered": [{"date": "20260628", "time": "0301"}],
            "totals": [72],
            "crit_avg": {
                "one_shot": 18,
                "context_drift": 18,
                "ai_control": 18,
                "prompt_clarity": 18,
            },
            "weakest": "one_shot",
            "strongest": "prompt_clarity",
            "trend_delta": 0.0,
            "smell_top": [],
            "proj_avg": {"demo": 72.0},
            "grade_dist": {"B": 1},
            "recent_imp": ["Name environment assumptions early."],
        }

        html = vibe.generate_growth_html(
            sig,
            learning={
                "open": 2,
                "high_open": 1,
                "by_domain": {"Docker": 1, "Oracle": 1},
                "review_candidates": [
                    {
                        "id": "LC-20260628-docker-logs",
                        "domain": "Docker",
                        "title": "Docker container log triage",
                        "severity": 4,
                    }
                ],
            },
        )

        self.assertIn("Domain Learning", html)
        self.assertIn("열린 Learning Card", html)
        self.assertIn("vibe learn next", html)
        self.assertIn("Docker container log triage", html)


if __name__ == "__main__":
    unittest.main()
