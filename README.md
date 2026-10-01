# Contest Analytics

Codeforces shows you a rating graph and a list of submissions, but it doesn't tell you much about *how* you practice: which topics you keep avoiding, what difficulty you're actually comfortable at, or which problems you gave up on. I built Contest Analytics to answer those questions for my own handle, and then made it work for any handle.

**Live:** https://contest-analytics.vercel.app

## What it does

Type in a Codeforces handle and you get a dashboard with:

- **Profile and summary:** rank, rating, total solved, contests played, average rating of solved problems.
- **Tag breakdown:** which topics you solve most, and which common topics barely show up in your accepted submissions.
- **Rating buckets:** how your solved problems are spread across difficulty (800–999, 1000–1199, …).
- **Activity:** problems solved and contests played per month.
- **Solved and unsolved tables:** searchable lists. The unsolved one shows problems you attempted but never got AC on, with your last verdict and number of tries. These are usually the best ones to go back to.
- **Recommendations:** a small ML model that suggests problems which should be challenging but doable for you (more on this below).
- **Global search:** search the whole Codeforces problemset by name, contest/index (like `1873B`), tag, or rating range.
- **Compare:** put two handles side by side and see common problems, problems only one of you solved, and shared strong topics.

## How the recommendations work

The recommender is a logistic regression model that predicts the chance you'll solve a given problem, based on 7 features from your history *before* that attempt: the problem's rating, your rating at the time, the gap between the two, how many problems you'd solved so far, the average rating of those, and your past success rate and experience with the problem's tags.

I trained it on 50 users rated roughly 950–1500, picked at random from one contest (about 14,500 attempted problems in total). Each user's history is split by time, so the model is always tested on attempts that came after the ones it learned from.

To recommend problems for you, it:

1. takes unattempted problems from 100 below to 400 above your current rating,
2. keeps the ones where your predicted solve chance is between 35% and 80% (not trivial, not hopeless),
3. takes at most 3 per rating so you get a mix, and returns the top 10.

It's a simple model trained on a small, low-rated sample, so treat it as a practice nudge, not an oracle. It works best for users under about 1600.

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy, MySQL, pandas, scikit-learn
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Recharts
- **Hosting:** Railway (API and MySQL), Vercel (frontend)

## Project structure

```text
Contest-Analytics/
├── app.py                     # entry point for uvicorn (loads backend/main.py)
├── config.example.yaml        # template for your local config.yaml (gitignored)
├── backend/
│   ├── main.py                # FastAPI app, CORS, error handling
│   ├── api/                   # one router per feature
│   │   ├── profile.py         # profile, solved/unsolved, stats, summary, dashboard
│   │   ├── compare.py
│   │   ├── problems.py        # global search and recommendations
│   │   └── tracked_handles.py
│   ├── services/
│   │   ├── codeforces_client.py   # talks to the Codeforces API, builds problem records
│   │   ├── profile_analytics.py   # tag stats, rating buckets, summary, activity
│   │   └── tracking.py            # saves searched handles to MySQL
│   ├── ml/                    # recommender + scripts to build the data set and train
│   ├── database.py, models.py, schemas.py, config.py
├── tests/
└── frontend/                  # React app
```

A note on the Codeforces API: it allows roughly one request every 2 seconds. `codeforces_client.py` spaces requests out, retries with backoff when it gets rate limited, and caches responses for 30 seconds. All of that state lives in memory, so **run the backend as a single worker** (don't pass `--workers`). Otherwise each worker throttles on its own and together they go over the limit.

## Running it locally

You need Python 3.10+, Node 18+, and optionally MySQL. The app works without a database; it just won't remember which handles were searched.

**1. Backend**

```bash
git clone https://github.com/mpssriram/Contest-Analytics.git
cd Contest-Analytics
pip install -r requirements.txt
```

To use MySQL, either set `DATABASE_URL`:

```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/codeforces
```

or copy `config.example.yaml` to `config.yaml`, fill in your details, and create the database it points to (`CREATE DATABASE codeforces;`). `config.yaml` is gitignored so your password stays local. `DATABASE_URL` wins if both are set. The table is created automatically on startup.

Then start the API:

```bash
python -m uvicorn app:app --reload --port 8000
```

Interactive docs are at http://127.0.0.1:8000/docs.

**2. Frontend**

```bash
cd frontend
npm install
cp .env.example .env      # sets VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

Open http://127.0.0.1:5173.

**Tests and ML scripts.** Run these from the project root:

```bash
python -m unittest discover -s tests -t .

python -m backend.ml.multi_data_process           # rebuild the training data from the handles list
python -m backend.ml.Multi_data_training_model    # retrain and save the model to backend/ml/saved/
```

The tests use fake Codeforces data, so they don't need internet access or a database.

## API

All routes are `GET` unless noted.

| Route | What it returns |
|---|---|
| `/api/dashboard/{handle}` | Everything the dashboard needs in one call |
| `/api/profile/{handle}` | Profile info |
| `/api/solved/{handle}` | Solved problems |
| `/api/unsolved/{handle}` | Attempted but unsolved problems |
| `/api/tag-stats/{handle}` | Solved count per tag |
| `/api/rating-stats/{handle}` | Solved count per rating bucket |
| `/api/summary/{handle}` | Summary numbers and observations |
| `/api/recommend/{handle}` | Recommended problems |
| `/api/problems/search` | Problemset search (`query`, `tag`, `min_rating`, `max_rating`, `limit`) |
| `/api/compare/{left}/{right}` | Side-by-side comparison |
| `/api/tracked-handles` | Recently searched handles |
| `POST /api/tracked-handles/{handle}` | Record a search |
| `/health`, `/api/health` | Health check |

## Deployment

- **Backend (Railway):** start command `uvicorn app:app --host 0.0.0.0 --port $PORT`. Set `DATABASE_URL` to the Railway MySQL URL, and `FRONTEND_URL` to your frontend's domain so CORS allows it.
- **Frontend (Vercel):** root directory `frontend`, build command `npm run build`, output `dist`. Set `VITE_API_BASE_URL` to the Railway URL.

## How I built this

The parts I wrote myself are the core of the backend: pulling data from the Codeforces API and turning it into solved/unsolved records and stats (`codeforces_client.py`, `profile_analytics.py`), and the ML pipeline, from collecting the data set to engineering the features, training, and evaluating the model.

I used AI tools as an assistant for the frontend UI, project scaffolding, deployment setup, refactoring and tests. I made the design decisions and I understand how every part fits together, but I didn't hand-write every line, and I'd rather say that up front.

## What I'd like to add next

- Better model features (time since last attempt, contest vs. practice) and training on a wider rating range
- Contest-by-contest performance trends
- A shared cache (e.g. Redis) so the API can run more than one worker
- Logins, so users can save their dashboards
