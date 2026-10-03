import unittest
from unittest.mock import MagicMock, patch

import requests

from backend.services.codeforces_client import CodeforcesAPIError, CodeforcesClient
from tests.fakes import fake_request


class SubmissionRecordTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(CodeforcesClient, "_request", classmethod(fake_request))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.source = CodeforcesClient("student")

    def test_solved_records_use_first_accept_and_newest_solve_first(self):
        records = self.source.solved_problem_records()

        self.assertEqual([record["id"] for record in records], ["4D", "1A"])
        first_a = records[1]
        self.assertEqual(first_a["attempts"], 4)
        self.assertEqual(first_a["language"], "C++")
        self.assertEqual(first_a["solvedAt"], "1970-01-01T00:06:40+00:00")
        self.assertEqual(first_a["url"], "https://codeforces.com/problemset/problem/1/A")

    def test_unsolved_records_use_latest_attempt_and_newest_first(self):
        records = self.source.unsolved_problem_records()

        self.assertEqual([record["id"] for record in records], ["2B", "5E"])
        self.assertEqual(records[0]["attempts"], 2)
        self.assertEqual(records[0]["verdict"], "WRONG_ANSWER")
        self.assertEqual(records[0]["language"], "C++")
        self.assertEqual(records[0]["lastTriedAt"], "1970-01-01T00:08:20+00:00")
        self.assertIsNone(records[1]["rating"])

    def test_ml_records_keep_training_semantics(self):
        solved = self.source.solved_problem_records_ML()
        unsolved = self.source.unsolved_problem_records_ML()

        self.assertEqual(
            solved,
            [
                {"id": "1A", "rating": 1200, "tags": ["dp"], "contestId": 1, "attempts": 4,
                 "solved": 1, "solvedAt": 400, "firstTriedAt": 100},
                {"id": "4D", "rating": 1500, "tags": ["math"], "contestId": 4, "attempts": 1,
                 "solved": 1, "solvedAt": 700, "firstTriedAt": 700},
            ],
        )
        # unsolved "firstTriedAt" is the first attempt (300), not the latest one (500)
        self.assertEqual(
            unsolved,
            [
                {"id": "2B", "rating": 1300, "tags": ["graphs"], "contestId": 2, "attempts": 2,
                 "solved": 0, "firstTriedAt": 300},
                {"id": "5E", "rating": None, "tags": ["strings"], "contestId": 5, "attempts": 1,
                 "solved": 0, "firstTriedAt": 50},
            ],
        )

    def test_solved_problem_ids_lists_unique_solved_ids(self):
        self.assertEqual(self.source.solved_problem_ids(), ["4D", "1A"])

    def test_empty_handle_is_rejected(self):
        with self.assertRaises(ValueError):
            CodeforcesClient("   ")


class SearchProblemsetTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(CodeforcesClient, "_request", classmethod(fake_request))
        patcher.start()
        self.addCleanup(patcher.stop)
        # start with an empty shared problem list
        for name, value in [("_problemset_cache", None), ("_rated_problemset_cache", None), ("_problemset_fetched_at", 0.0)]:
            patcher = patch(f"backend.services.codeforces_client.{name}", value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_called_on_class_filters_by_query_and_rating(self):
        results = CodeforcesClient.search_problemset(query="graph", min_rating=1000)

        self.assertEqual([problem["id"] for problem in results], ["8B"])
        self.assertEqual(results[0]["solvedCount"], 20)

    def test_rating_filter_drops_unrated_problems(self):
        results = CodeforcesClient.search_problemset(max_rating=3500)
        self.assertNotIn("9C", [problem["id"] for problem in results])


class RequestErrorTests(unittest.TestCase):
    def setUp(self):
        patcher = patch("backend.services.codeforces_client._response_cache", {})
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = patch.object(CodeforcesClient, "_wait_for_request_slot", classmethod(lambda cls: None))
        patcher.start()
        self.addCleanup(patcher.stop)
        # keep these tests away from the real MySQL cache
        for name, value in [("load", lambda path, params: None), ("save", lambda path, params, payload: None)]:
            patcher = patch(f"backend.services.response_store.{name}", value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_non_json_response_becomes_codeforces_error(self):
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.side_effect = requests.JSONDecodeError("Expecting value", "<html>", 0)

        with patch("backend.services.codeforces_client.requests.get", return_value=response):
            with self.assertRaises(CodeforcesAPIError) as context:
                CodeforcesClient._request("/user.info", {"handles": "student"})

        self.assertEqual(context.exception.status_code, 502)

    def test_unknown_handle_400_becomes_404(self):
        response = MagicMock(status_code=400)
        response.json.return_value = {"status": "FAILED", "comment": "handles: User with handle zz not found"}
        response.raise_for_status.side_effect = requests.HTTPError(response=response)

        with patch("backend.services.codeforces_client.requests.get", return_value=response):
            with self.assertRaises(CodeforcesAPIError) as context:
                CodeforcesClient._request("/user.info", {"handles": "zz"})

        self.assertEqual(context.exception.status_code, 404)
        self.assertIn("not found", context.exception.message)


if __name__ == "__main__":
    unittest.main()
