# Contest Analytics

Contest Analytics is a Codeforces analytics project with:
- a beginner-friendly FastAPI backend built on top of the existing Python logic in `URLextract.py` and `Data_dataframe.py`
- a MySQL database for tracking searched handles with SQLAlchemy
- a React + Vite + Tailwind CSS frontend for searching a handle and viewing charts, stats, and solved problems

## Folder Structure

```text
Contest-Analytics/
|-- app.py
|-- database.py
|-- URLextract.py
|-- Data_dataframe.py
|-- models.py
|-- schemas.py
|-- requirements.txt
|-- frontend/
|   |-- package.json
|   |-- .env.example
|   |-- src/
|   |   |-- components/
|   |   |-- hooks/
|   |   |-- pages/
|   |   |-- services/
|   |   |-- types/
|   |   |-- utils/
|   |   |-- App.tsx
|   |   |-- main.tsx
|   |   `-- index.css
|   `-- public/
`-- README.md
```

## Backend Overview

The existing Python files were preserved and adapted instead of being replaced.

- `URLextract.py`
  Handles raw Codeforces API fetching and returns reusable Python data structures.
- `Data_dataframe.py`
  Builds analytics from solved problems, tag counts, rating buckets, activity trend, and summary insights.
- `database.py`
  Contains the MySQL connection, SQLAlchemy session, and table creation helper.
- `models.py`
  Defines the `tracked_handles` table.
- `app.py`
  Exposes the data through FastAPI routes with CORS enabled for the frontend and saves tracked searches.

## API Routes

Base URL: `http://127.0.0.1:8000`

- `GET /api/health`
- `GET /api/tracked-handles`
- `POST /api/tracked-handles/{handle}`
- `GET /api/profile/{handle}`
- `GET /api/solved/{handle}`
- `GET /api/tag-stats/{handle}`
- `GET /api/rating-stats/{handle}`
- `GET /api/summary/{handle}`

FastAPI docs will be available at:
- `http://127.0.0.1:8000/docs`

## Frontend Overview

The frontend lives in `frontend/` and uses:
- React
- Vite
- Tailwind CSS
- Recharts

Important frontend files:
- `frontend/src/services/api.ts`
  Contains the backend API calls.
- `frontend/src/pages/Home.tsx`
  Landing page with the search hero.
- `frontend/src/pages/Dashboard.tsx`
  Dashboard page that renders charts, stats, and the solved problems table.

## Run The Backend

1. Create the MySQL database:

```sql
CREATE DATABASE contest_analytics;
```

2. Update your MySQL credentials in `database.py`:

```python
MYSQL_USERNAME = "your_username"
MYSQL_PASSWORD = "your_password"
MYSQL_HOST = "localhost"
MYSQL_DATABASE = "contest_analytics"
```

3. Create and activate a virtual environment if you want one.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Create the table:

```bash
py database.py
```

6. Start FastAPI:

```bash
uvicorn app:app --reload --port 8000
```

Backend URL:
- `http://127.0.0.1:8000`

## Run The Frontend

1. Move into the frontend folder:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Copy the example env if needed and keep the API URL pointed at the backend:

```bash
copy .env.example .env
```

4. Start the Vite dev server:

```bash
npm run dev
```

Frontend URL:
- `http://127.0.0.1:5173`

## Frontend To Backend Connection

The frontend expects this backend by default:
- `VITE_API_BASE_URL=http://127.0.0.1:8000`

That value is read in:
- `frontend/src/services/api.ts`

If you later change backend host or port, update the env value and restart the frontend dev server.

## Cloud Deployment

Recommended setup:
- Backend + MySQL: Railway
- Frontend: Vercel

Backend environment variables:
- `DATABASE_URL`
- `FRONTEND_URL`

Optional local-style backend variables if `DATABASE_URL` is not set:
- `MYSQL_USERNAME`
- `MYSQL_PASSWORD`
- `MYSQL_HOST`
- `MYSQL_DATABASE`

Frontend environment variable:
- `VITE_API_BASE_URL`

Example values:

```env
# Railway backend
DATABASE_URL=mysql+pymysql://username:password@host/database
FRONTEND_URL=https://your-frontend-domain.vercel.app

# Vercel frontend
VITE_API_BASE_URL=https://your-backend-domain.up.railway.app
```

Railway start command:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port $PORT
```

## Notes For Future Backend Expansion

If you want to extend the integration later, the cleanest places are:
- `URLextract.py` for additional raw Codeforces fetching
- `Data_dataframe.py` for new analytics calculations
- `models.py` for new database tables
- `app.py` for new API endpoints
- `frontend/src/services/api.ts` for new frontend calls

This keeps the fetch layer, analytics layer, database layer, and UI layer separate and beginner-friendly.
