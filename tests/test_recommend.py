import unittest
from unittest.mock import patch

import numpy as np


class FakeSource:
    def __init__(self, handle):
        self.handle = handle

    def solved_problem_records_ML(self):
        return [
            {"id": "1A", "rating": 1200, "tags": ["dp", "math"], "solved": 1, "firstTriedAt": 100},
            {"id": "2B", "rating": 1400, "tags": ["dp"], "solved": 1, "firstTriedAt": 300},
        ]

    def unsolved_problem_records_ML(self):
        return [
            {"id": "3C", "rating": 1300, "tags": ["math", "graphs"], "solved": 0, "firstTriedAt": 200}
        ]

    def user_rating_history(self):
        return [
            {"ratingUpdateTimeSeconds": 90, "newRating": 1250},
            {"ratingUpdateTimeSeconds": 250, "newRating": 1350},
        ]


class RecordingScaler:
    def __init__(self):
        self.rows = None

    def transform(self, rows):
        self.rows = rows.copy()
        return rows.to_numpy()


class FakeModel:
    def predict_proba(self, rows):
        probabilities = {1500: 0.70, 1600: 0.60, 1700: 0.90, 1450: 0.40}
        positive = np.array([probabilities[int(row[0])] for row in rows])
        return np.column_stack((1 - positive, positive))


class RecommendTests(unittest.TestCase):
    def test_builds_exact_features_and_filters_ranked_candidates(self):
        from backend.ml import recommend as recommend_module

        scaler = RecordingScaler()
        problems = [
            {"id": "1A", "name": "Attempted", "rating": 1500, "tags": ["dp"], "url": "attempted"},
            {"id": "4D", "name": "Best match", "rating": 1500, "tags": ["dp", "graphs", "new"], "url": "best"},
            {"id": "5E", "name": "Second match", "rating": 1600, "tags": ["math"], "url": "second"},
            {"id": "6F", "name": "Too likely", "rating": 1700, "tags": ["dp"], "url": "high"},
            {"id": "7G", "name": "Too unlikely", "rating": 1450, "tags": ["dp"], "url": "low"},
            {"id": "8H", "name": "Too easy", "rating": 1200, "tags": ["dp"], "url": "easy"},
        ]
        with (
            patch.object(recommend_module, "CodeforcesClient", FakeSource),
            patch.object(recommend_module, "MODEL", FakeModel()),
            patch.object(recommend_module, "SCALER", scaler),
            patch.object(recommend_module, "_get_problemset", return_value=problems),
        ):
            result = recommend_module.recommend("student", top_n=10)

        # Candidate 4D, calculated by hand:
        # rating = 1500
        # previous solved count = 2
        # previous average solved rating = (1200 + 1400) / 2 = 1300
        # average tag success = (dp 2/2 + graphs 0/1 + new 0) / 3 = 1/3
        # average tag attempts = (dp 2 + graphs 1 + new 0) / 3 = 1
        # current user rating = 1350
        # rating gap = 1500 - 1350 = 150
        self.assertEqual(
            scaler.rows.iloc[0].tolist(),
            [1500, 2, 1300, 1 / 3, 1, 1350, 150],
        )
        self.assertEqual([problem["id"] for problem in result], ["4D", "5E"])
        self.assertEqual([problem["probability"] for problem in result], [0.7, 0.6])
        self.assertNotIn("1A", [problem["id"] for problem in result])


if __name__ == "__main__":
    unittest.main()
