import time
import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend import database
from backend.models import CachedResponse
from backend.services import codeforces_client, response_store
from backend.services.codeforces_client import CodeforcesClient

PAYLOAD = {"status": "OK", "result": [{"handle": "student", "rating": 1200}]}


class ResponseStoreTests(unittest.TestCase):
    def setUp(self):
        # a throwaway in-memory database instead of the real MySQL
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        database.Base.metadata.create_all(bind=engine)
        patcher = patch.object(database, "SessionLocal", sessionmaker(bind=engine))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_saved_reply_comes_back(self):
        response_store.save("/user.info", {"handles": "student"}, PAYLOAD)

        self.assertEqual(response_store.load("/user.info", {"handles": "student"}), PAYLOAD)
        self.assertIsNone(response_store.load("/user.info", {"handles": "someone_else"}))

    def test_saving_again_replaces_the_old_copy(self):
        response_store.save("/user.info", {"handles": "student"}, {"status": "OK", "result": []})
        response_store.save("/user.info", {"handles": "student"}, PAYLOAD)

        with database.SessionLocal() as db:
            self.assertEqual(db.query(CachedResponse).count(), 1)
        self.assertEqual(response_store.load("/user.info", {"handles": "student"}), PAYLOAD)

    def test_old_reply_is_ignored_and_cleaned_up(self):
        response_store.save("/user.info", {"handles": "student"}, PAYLOAD)
        with database.SessionLocal() as db:
            db.query(CachedResponse).update({"fetched_at": time.time() - 2 * 24 * 60 * 60})
            db.commit()

        self.assertIsNone(response_store.load("/user.info", {"handles": "student"}))
        response_store.delete_old()
        with database.SessionLocal() as db:
            self.assertEqual(db.query(CachedResponse).count(), 0)

    def test_fetched_at_is_whole_seconds(self):
        # MySQL FLOAT rounded unix times by hours, which broke the 10 minute expiry.
        # SQLite would not show that bug, so check the column type itself
        from sqlalchemy import BigInteger

        self.assertIsInstance(CachedResponse.__table__.c.fetched_at.type, BigInteger)

    def test_problem_list_is_not_stored(self):
        response_store.save("/problemset.problems", {}, PAYLOAD)

        self.assertIsNone(response_store.load("/problemset.problems", {}))

    def test_no_database_means_no_cache(self):
        with patch.object(database, "SessionLocal", None):
            response_store.save("/user.info", {"handles": "student"}, PAYLOAD)
            self.assertIsNone(response_store.load("/user.info", {"handles": "student"}))

    def test_request_uses_the_database_copy_without_calling_codeforces(self):
        response_store.save("/user.info", {"handles": "student"}, PAYLOAD)

        with patch.object(codeforces_client, "_response_cache", {}), \
                patch("backend.services.codeforces_client.requests.get") as fake_get:
            result = CodeforcesClient._request("/user.info", {"handles": "student"})

        self.assertEqual(result, PAYLOAD)
        fake_get.assert_not_called()

    def test_fresh_reply_from_codeforces_gets_saved(self):
        response = MagicMock()
        response.raise_for_status.return_value = None
        response.json.return_value = PAYLOAD

        with patch.object(codeforces_client, "_response_cache", {}), \
                patch.object(CodeforcesClient, "_wait_for_request_slot", classmethod(lambda cls: None)), \
                patch("backend.services.codeforces_client.requests.get", return_value=response):
            CodeforcesClient._request("/user.info", {"handles": "student"})

        self.assertEqual(response_store.load("/user.info", {"handles": "student"}), PAYLOAD)


class MemoryCacheLimitTests(unittest.TestCase):
    def test_memory_cache_never_grows_past_the_limit(self):
        with patch.object(codeforces_client, "_response_cache", {}):
            for number in range(codeforces_client.MAX_CACHED_RESPONSES + 50):
                CodeforcesClient._store_cached_payload("/user.info", {"handles": f"user{number}"}, PAYLOAD)

            self.assertEqual(len(codeforces_client._response_cache), codeforces_client.MAX_CACHED_RESPONSES)
            # the newest one is kept, the oldest ones were dropped
            self.assertIsNotNone(CodeforcesClient._get_cached_payload("/user.info", {"handles": "user149"}))
            self.assertIsNone(CodeforcesClient._get_cached_payload("/user.info", {"handles": "user0"}))


if __name__ == "__main__":
    unittest.main()
