
from pathlib import Path
import sys

import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from URLextract import Get_data
 
# rating window around the user's rating
RATING_BELOW = 100
RATING_ABOVE = 400
# used as the window centre when the user has no rated contests yet
DEFAULT_RATING = 800
# "challenging but doable" probability band
MIN_PROBABILITY = 0.35
MAX_PROBABILITY = 0.8
PER_RATING = 3
 
# same 7 columns, same order as in training
FEATURES = [
    "rating",
    "previous_solved_count",
    "previous_avg_solved_rating",
    "previous_avg_tag_success_rate",
    "previous_avg_tag_attempted",
    "user_rating_at_time",
    "rating_gap",
]
 
# load the trained model and scaler ONCE, when this file is imported
SAVED_DIR = Path(__file__).parent / "saved"
_MODEL_ERROR = None
try:
    MODEL = joblib.load(SAVED_DIR / "model.joblib")
    SCALER = joblib.load(SAVED_DIR / "scaler.joblib")
except FileNotFoundError as error:
    MODEL = None
    SCALER = None
    _MODEL_ERROR = error
 
# all rated Codeforces problems, fetched once and kept in memory
_PROBLEMSET_CACHE = None
 
 
def _get_problemset(source):
    # source is a Get_data object; calling through it works whether
    # _request / problem_url are normal methods or static methods
    global _PROBLEMSET_CACHE
    if _PROBLEMSET_CACHE is None:
        payload = source._request("/problemset.problems", {})
        _PROBLEMSET_CACHE = []
        for problem in payload.get("result", {}).get("problems", []):
            contest_id = problem.get("contestId")
            index = problem.get("index")
            rating = problem.get("rating")
            # skip unrated problems and problems without an id
            if contest_id is None or index is None or rating is None:
                continue

            if "*special" in problem.get("tags", []):
                continue

            problem_id = f"{contest_id}{index}"
            _PROBLEMSET_CACHE.append({
                "id": problem_id,
                "name": problem.get("name", problem_id),
                "rating": rating,
                "tags": problem.get("tags", []),
                "url": source.problem_url(contest_id, index),
            })
    return _PROBLEMSET_CACHE
 
 
def _history_features(source):
    # the user's full history: solved + attempted-but-unsolved
    solved = source.solved_problem_records_ML()
    unsolved = source.unsolved_problem_records_ML()
    history = solved + unsolved
 
    # only rated problems are used for features (same as data_set.py dropna)
    rated_history = [problem for problem in history if problem.get("rating") is not None]
 
    # previous_solved_count and previous_avg_solved_rating
    solved_history = [problem for problem in rated_history if problem["solved"] == 1]
    solved_count = len(solved_history)
    if solved_count != 0:
        average_solved_rating = sum(problem["rating"] for problem in solved_history) / solved_count
    else:
        average_solved_rating = 0
 
    # per-tag solved and attempted counts
    tag_solved = {}
    tag_attempted = {}
    for problem in rated_history:
        for tag in problem.get("tags", []):
            tag_attempted[tag] = tag_attempted.get(tag, 0) + 1
            if problem["solved"] == 1:
                tag_solved[tag] = tag_solved.get(tag, 0) + 1
 
    # current rating = newRating of the latest contest, 0 if never rated
    rating_history = sorted(
        source.user_rating_history(),
        key=lambda update: update["ratingUpdateTimeSeconds"],
    )
    if rating_history:
        user_rating = rating_history[-1]["newRating"]
    else:
        user_rating = 0
 
    return history, solved_count, average_solved_rating, tag_solved, tag_attempted, user_rating
 
 
def _candidate_features(candidate, solved_count, average_solved_rating, tag_solved, tag_attempted, user_rating):
    tags = candidate.get("tags", [])
 
    # success rate per tag; a tag never attempted counts as 0
    success_rates = []
    for tag in tags:
        if tag_attempted.get(tag, 0) != 0:
            success_rates.append(tag_solved.get(tag, 0) / tag_attempted[tag])
        else:
            success_rates.append(0)
 
    # attempted count per tag; a tag never attempted counts as 0
    attempts = []
    for tag in tags:
        attempts.append(tag_attempted.get(tag, 0))
 
    return {
        "rating": candidate["rating"],
        "previous_solved_count": solved_count,
        "previous_avg_solved_rating": average_solved_rating,
        "previous_avg_tag_success_rate": sum(success_rates) / len(success_rates) if success_rates else 0,
        "previous_avg_tag_attempted": sum(attempts) / len(attempts) if attempts else 0,
        "user_rating_at_time": user_rating,
        "rating_gap": candidate["rating"] - user_rating,
    }
 
 
def recommend(handle, top_n=10):
    if MODEL is None or SCALER is None:
        raise FileNotFoundError(
            "Saved model files are missing. Run Multi_data_training_model.py with SAVE_MODEL = True."
        ) from _MODEL_ERROR
 
    source = Get_data(handles=handle)
    history, solved_count, average_solved_rating, tag_solved, tag_attempted, user_rating = _history_features(source)
 
    # every problem the user has already attempted (solved or not) is excluded
    attempted_ids = {problem["id"] for problem in history}
 
    # window centre: user's rating, or 800 if the user has no rated contests
    # (only the window uses this; the feature user_rating_at_time stays 0, as in training)
    if user_rating > 0:
        window_center = user_rating
    else:
        window_center = DEFAULT_RATING
 
    candidates = [
        problem for problem in _get_problemset(source)
        if problem["id"] not in attempted_ids
        and window_center - RATING_BELOW <= problem["rating"] <= window_center + RATING_ABOVE
    ]
    if not candidates or top_n <= 0:
        return []
 
    # build the 7 features for every candidate, in training column order
    rows = []
    for problem in candidates:
        rows.append(_candidate_features(problem, solved_count, average_solved_rating, tag_solved, tag_attempted, user_rating))
    features = pd.DataFrame(rows, columns=FEATURES)
 
    # same scaler as training, then probability of "solved"
    probabilities = MODEL.predict_proba(SCALER.transform(features))[:, 1]
 
    # keep the "challenging but doable" band
    recommendations = []
    for problem, probability in zip(candidates, probabilities):
        probability = float(probability)
        if MIN_PROBABILITY <= probability <= MAX_PROBABILITY:
            recommendations.append({
                "id": problem["id"],
                "name": problem["name"],
                "rating": problem["rating"],
                "tags": problem["tags"],
                "probability": round(probability, 3),
                "url": problem["url"],
            })
 
    # highest probability first
    recommendations.sort(key=lambda problem: problem["probability"], reverse=True)

    # take at most PER_RATING problems from each rating, so difficulties are mixed
    per_rating_count = {}
    mixed = []
    for problem in recommendations:
        r = problem["rating"]
        if per_rating_count.get(r, 0) < PER_RATING:
            mixed.append(problem)
            per_rating_count[r] = per_rating_count.get(r, 0) + 1

    # easier ones first
    mixed.sort(key=lambda problem: problem["rating"])
    return mixed[:top_n]

if __name__ == "__main__":
    results = recommend("Sriracodezr")
    print("recommendations:", len(results))
    for r in results:
        print(r["id"], r["name"], r["rating"], r["probability"])

