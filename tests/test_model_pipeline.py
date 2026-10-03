import unittest

import numpy as np
import pandas as pd

from backend.ml.evaluation import Evaluation
from backend.ml.model_pipeline import ModelPipeline

FEATURES = [
    "rating",
    "previous_solved_count",
    "previous_avg_solved_rating",
    "previous_avg_tag_success_rate",
    "previous_avg_tag_attempted",
    "user_rating_at_time",
    "rating_gap",
]


def fake_rows(count, seed):
    # like the real data: most attempts end solved, and harder-than-you problems less often
    random = np.random.default_rng(seed)
    user_rating = random.integers(800, 2000, count)
    gap = random.integers(-400, 600, count)
    solve_chance = 1 / (1 + np.exp((gap - 500) / 150))
    rows = pd.DataFrame({
        "rating": user_rating + gap,
        "previous_solved_count": random.integers(0, 600, count),
        "previous_avg_solved_rating": user_rating - 100,
        "previous_avg_tag_success_rate": random.uniform(0.6, 1.0, count),
        "previous_avg_tag_attempted": random.uniform(0, 50, count),
        "user_rating_at_time": user_rating,
        "rating_gap": gap,
    })
    solved = pd.Series((random.uniform(0, 1, count) < solve_chance).astype(int))
    return rows[FEATURES], solved


class CalibrationTests(unittest.TestCase):
    def test_probabilities_match_how_often_problems_are_solved(self):
        x_train, y_train = fake_rows(6000, seed=1)
        x_validation, y_validation = fake_rows(3000, seed=2)
        x_test, y_test = fake_rows(3000, seed=3)

        pipeline = ModelPipeline()
        pipeline.model_trainning(x_train, y_train, x_validation, y_validation, x_test, y_test)
        y_prob, _ = pipeline.test_probabilities(x_test, y_test)

        # before calibration, class_weight='balanced' put the average far below the real rate
        self.assertGreater(y_test.mean(), 0.8)
        self.assertAlmostEqual(y_prob.mean(), y_test.mean(), delta=0.03)

        # and the "60-80%" band should really be solved about 60-80% of the time
        band = (y_prob >= 0.6) & (y_prob < 0.8)
        self.assertGreater(band.sum(), 50)
        self.assertTrue(0.55 <= y_test[band].mean() <= 0.85)


class BrierScoreTests(unittest.TestCase):
    def test_brier_score(self):
        perfect = Evaluation(y_prob=[1.0, 0.0], y_true=[1, 0])
        unsure = Evaluation(y_prob=[0.5, 0.5], y_true=[1, 0])
        wrong = Evaluation(y_prob=[0.0, 1.0], y_true=[1, 0])

        self.assertEqual(perfect.brier_score(), 0)
        self.assertEqual(unsure.brier_score(), 0.25)
        self.assertEqual(wrong.brier_score(), 1)


if __name__ == "__main__":
    unittest.main()
