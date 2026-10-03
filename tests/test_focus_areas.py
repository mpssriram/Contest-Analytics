import unittest
from unittest.mock import patch

from backend.services import codeforces_client
from backend.services.codeforces_client import CodeforcesAPIError, CodeforcesClient
from backend.services.profile_analytics import ProfileAnalytics


def problems(count, rating, tags):
    return [{"rating": rating, "tags": list(tags)} for _ in range(count)]


# 100 problems at 1200: 40 constructive, 10 graphs, 50 greedy
LEVEL_PROBLEMSET = (
    problems(40, 1200, ["constructive algorithms"])
    + problems(10, 1200, ["graphs"])
    + problems(50, 1200, ["greedy"])
    + problems(100, 3300, ["dp"])
)


class FakeSource:
    def __init__(self, rating, solved):
        self.handle = "student"
        self._rating = rating
        self._solved = solved

    def user_info(self):
        return {"handle": "student", "rating": self._rating}

    def solved_problem_records(self):
        return self._solved


def focus_for(rating, solved, problemset=LEVEL_PROBLEMSET):
    with patch.object(CodeforcesClient, "rated_problemset", classmethod(lambda cls: problemset)):
        return ProfileAnalytics(source=FakeSource(rating, solved)).focus_areas()


class FocusAreasTests(unittest.TestCase):
    def test_new_user_without_enough_solves(self):
        focus = focus_for(0, problems(10, 800, ["greedy"]))

        self.assertFalse(focus["enoughData"])
        self.assertEqual(focus["underPracticed"], [])
        self.assertEqual((focus["levelLow"], focus["levelHigh"]), (800, 1200))

    def test_typical_user_gets_gaps_ceilings_and_comfortable(self):
        # rating 1100 -> level 1000-1400
        solved = (
            problems(40, 1200, ["greedy"])  # 40 solves at their level, all greedy
            + problems(3, 800, ["graphs"])  # graphs only at 800
            + problems(10, 1600, ["math"])  # 10 harder solves set the overall level
        )
        focus = focus_for(1100, solved)

        self.assertTrue(focus["enoughData"])
        self.assertEqual((focus["levelLow"], focus["levelHigh"]), (1000, 1400))
        self.assertEqual(focus["comparedAgainst"], "level")
        self.assertEqual(focus["comparedSolves"], 40)
        self.assertEqual(
            focus["underPracticed"],
            [
                {"tag": "constructive algorithms", "levelShare": 0.4, "yourShare": 0.0},
                {"tag": "graphs", "levelShare": 0.1, "yourShare": 0.0},
            ],
        )
        self.assertEqual(focus["overallComfortable"], 1600)
        # both sit 300+ below the overall 1600, lowest first
        self.assertEqual(
            focus["ceilings"],
            [
                {"tag": "graphs", "comfortableRating": 800, "solved": 3},
                {"tag": "greedy", "comfortableRating": 1200, "solved": 40},
            ],
        )
        self.assertEqual(focus["comfortable"][0], {"tag": "math", "comfortableRating": 1600, "solved": 10})
        self.assertFalse(focus["atTop"])

    def test_few_solves_at_level_compares_against_everything(self):
        solved = problems(5, 1200, ["greedy"]) + problems(20, 900, ["greedy"])
        focus = focus_for(1100, solved)

        self.assertEqual(focus["comparedAgainst"], "all")
        self.assertEqual(focus["comparedSolves"], 25)

    def test_rare_tags_are_never_flagged(self):
        # divide and conquer never shows up at this level, so it must not be advice
        solved = problems(40, 1200, ["greedy", "constructive algorithms", "graphs"])
        focus = focus_for(1100, solved)

        flagged = [item["tag"] for item in focus["underPracticed"] + focus["ceilings"]]
        self.assertNotIn("divide and conquer", flagged)

    def test_top_user_is_at_the_top(self):
        solved = problems(40, 3300, ["dp"])
        focus = focus_for(3700, solved)

        self.assertEqual((focus["levelLow"], focus["levelHigh"]), (3100, 3500))
        self.assertEqual(focus["underPracticed"], [])
        self.assertTrue(focus["atTop"])

    def test_unrated_user_uses_middle_solved_rating(self):
        solved = problems(15, 1000, ["greedy"]) + problems(15, 1400, ["greedy"])
        focus = focus_for(0, solved)

        self.assertEqual((focus["levelLow"], focus["levelHigh"]), (1300, 1700))

    def test_problem_list_failure_keeps_dashboard_working(self):
        def fail(cls):
            raise CodeforcesAPIError("down", status_code=502)

        with patch.object(CodeforcesClient, "rated_problemset", classmethod(fail)):
            focus = ProfileAnalytics(source=FakeSource(1100, problems(30, 1200, ["greedy"]))).focus_areas()

        self.assertTrue(focus["enoughData"])
        self.assertFalse(focus["available"])


class RatedProblemsetTests(unittest.TestCase):
    def setUp(self):
        for name, value in [("_problemset_cache", None), ("_problemset_fetched_at", 0.0)]:
            patcher = patch.object(codeforces_client, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_downloads_once_and_skips_unrated_and_special(self):
        payload = {"status": "OK", "result": {"problems": [
            {"contestId": 1, "index": "A", "name": "Rated", "rating": 800, "tags": ["math"]},
            {"contestId": 1, "index": "B", "name": "Unrated", "tags": ["math"]},
            {"contestId": 1, "index": "C", "name": "Special", "rating": 900, "tags": ["*special"]},
        ]}}
        calls = []

        def fake_request(cls, path, params):
            calls.append(path)
            return payload

        with patch.object(CodeforcesClient, "_request", classmethod(fake_request)):
            first = CodeforcesClient.rated_problemset()
            second = CodeforcesClient.rated_problemset()

        self.assertEqual([problem["id"] for problem in first], ["1A"])
        self.assertIs(first, second)
        self.assertEqual(calls, ["/problemset.problems"])


if __name__ == "__main__":
    unittest.main()
