import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend import main as app_module
from backend.database import get_db
from backend.services.codeforces_client import CodeforcesClient
from tests.fakes import fake_request


class ApiRouteTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(CodeforcesClient, "_request", classmethod(fake_request))
        patcher.start()
        self.addCleanup(patcher.stop)

        app_module.app.dependency_overrides[get_db] = lambda: None
        self.addCleanup(app_module.app.dependency_overrides.clear)
        self.client = TestClient(app_module.app, raise_server_exceptions=False)

    def test_handle_routes_return_200(self):
        for path in [
            "/health",
            "/api/health",
            "/api/profile/student",
            "/api/solved/student",
            "/api/unsolved/student",
            "/api/tag-stats/student",
            "/api/rating-stats/student",
            "/api/summary/student",
            "/api/dashboard/student",
            "/api/compare/student/other",
            "/api/tracked-handles",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, response.text)

    def test_global_search(self):
        response = self.client.get("/api/problems/search", params={"query": "graph", "limit": 5})

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual([problem["id"] for problem in response.json()], ["8B"])

    def test_dashboard_shape(self):
        body = self.client.get("/api/dashboard/student").json()

        self.assertEqual(
            set(body),
            {"profile", "summary", "tagStats", "ratingStats", "solvedProblems", "unsolvedProblems"},
        )
        self.assertEqual(body["summary"]["totalSolved"], 2)
        self.assertEqual(body["summary"]["totalUnsolvedTried"], 2)
        self.assertEqual(body["summary"]["observations"], body["summary"]["recommendations"])
        self.assertIsNone(body["summary"]["trackedHandle"])

    def test_unknown_handle_is_404(self):
        response = self.client.get("/api/profile/missing")

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.json()["detail"])

    def test_blank_handle_is_400(self):
        response = self.client.get("/api/profile/%20")

        self.assertEqual(response.status_code, 400)

    def test_tracking_without_database_is_503(self):
        response = self.client.post("/api/tracked-handles/student")

        self.assertEqual(response.status_code, 503)

    def test_unexpected_error_is_500_with_cors_header(self):
        with patch.object(CodeforcesClient, "user_info", side_effect=RuntimeError("boom")):
            response = self.client.get(
                "/api/profile/student", headers={"Origin": "http://localhost:5173"}
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Unexpected server error.")
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:5173")


if __name__ == "__main__":
    unittest.main()
