# Contest Analytics

Contest Analytics is a full-stack Codeforces analytics website that lets users search a handle and explore problem-solving insights through a clean dashboard. The project combines a FastAPI backend, MySQL-based search tracking, and a React frontend to present profile stats, tag trends, rating-wise breakdowns, activity patterns, and problem tables in a portfolio-ready format.

The project was built with AI-assisted development for parts of the scaffolding, UI refinement, and integration support, while the core backend analytics and data-processing logic in `URLextract.py` and `Data_dataframe.py` was implemented by me.

## Features

- Search any Codeforces handle and load a dedicated analytics dashboard
- View profile information such as handle, rank, rating, max rating, avatar, country, and organization
- See summary metrics including total solved problems, total contests, average problem rating, and most solved tag
- Explore chart-based analytics for tag distribution, rating buckets, and recent activity
- Review solved problems in a searchable and filterable table
- Review unsolved attempted problems and jump back to the original Codeforces problem page
- Track searched handles with MySQL for lightweight backend metadata
- Use the app through a deployed frontend on Vercel and deployed backend on Railway

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- Pandas
- Requests

### Frontend

- React
- Vite
- Tailwind CSS
- Recharts
- React Router

### Deployment

- Railway for backend and MySQL
- Vercel for frontend

## Project Structure

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
|   |-- vercel.json
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

The backend is organized into small, beginner-friendly layers:

- `URLextract.py`
  Fetches raw Codeforces data and formats reusable records for profile data, solved problems, unsolved attempts, and rating history.
- `Data_dataframe.py`
  Builds the analytics layer, including tag statistics, rating buckets, summary metrics, strongest and weakest topics, and activity trends.
- `database.py`
  Configures the SQLAlchemy engine, database session, and optional MySQL connection for tracked handle storage.
- `models.py`
  Defines the `tracked_handles` table.
- `schemas.py`
  Defines response schemas used by FastAPI.
- `app.py`
  Exposes the API routes, configures CORS, and connects analytics + database behavior.

## Frontend Overview

The frontend lives in `frontend/` and is designed as a responsive, component-based dashboard.

Key frontend areas:

- `frontend/src/pages/Home.tsx`
  Landing page with the project hero and handle search
- `frontend/src/pages/Dashboard.tsx`
  Dashboard page that renders cards, charts, tables, and insights
- `frontend/src/services/api.ts`
  Centralized API layer for backend requests
- `frontend/src/components/`
  Reusable UI components such as cards, charts, tables, and search controls

## API Routes

Base backend URL in local development:

```text
http://127.0.0.1:8000
```

Core routes:

- `GET /health`
- `GET /api/health`
- `GET /api/profile/{handle}`
- `GET /api/solved/{handle}`
- `GET /api/unsolved/{handle}`
- `GET /api/tag-stats/{handle}`
- `GET /api/rating-stats/{handle}`
- `GET /api/summary/{handle}`

Database-backed routes:

- `GET /api/tracked-handles`
- `POST /api/tracked-handles/{handle}`

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## Local Setup

### 1. Clone the project

```bash
git clone <your-repo-url>
cd Contest-Analytics
```

### 2. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the MySQL database

```sql
CREATE DATABASE contest_analytics;
```

### 4. Configure backend environment variables

You can configure the database in either of these two ways.

Using a full database URL:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/contest_analytics
FRONTEND_URL=http://127.0.0.1:5173
```

Or using individual MySQL variables:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=contest_analytics
FRONTEND_URL=http://127.0.0.1:5173
```

### 5. Start the backend

```bash
python -m uvicorn app:app --reload --port 8000
```

### 6. Install frontend dependencies

```bash
cd frontend
npm install
```

### 7. Configure frontend environment variables

Create a `.env` file inside `frontend/`:

```env
VITE_API_URL=http://127.0.0.1:8000
```

### 8. Start the frontend

```bash
npm run dev
```

Local app URLs:

- Frontend: `http://127.0.0.1:5173`
- Backend: `http://127.0.0.1:8000`

## Deployment

### Backend and Database

Railway is used for the FastAPI backend and MySQL database.

Recommended backend variables:

```env
DATABASE_URL=mysql+pymysql://username:password@host:port/database
FRONTEND_URL=https://your-frontend-domain.vercel.app
```

Railway start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Frontend

Vercel is used for the React frontend.

Recommended Vercel settings:

- Root Directory: `frontend`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`

Frontend environment variable:

```env
VITE_API_URL=https://your-backend-domain.up.railway.app
```

## My Contribution

This project reflects both my own implementation work and responsible AI-assisted development.

### What I implemented directly

- The core Codeforces data-fetching and analytics logic in `URLextract.py` and `Data_dataframe.py`
- The backend data flow that transforms raw Codeforces API responses into profile stats, solved-problem records, tag counts, rating distributions, and summary insights
- The integration direction for how analytics data should be exposed and used in the application

### Where AI-assisted development was used

- Project scaffolding and cleanup for parts of the FastAPI and frontend structure
- UI refinement and component organization in the React dashboard
- Refactoring support, deployment setup help, and integration polishing
- Documentation and formatting improvements

In other words, I did not manually write every line in the repository. However, the project idea, backend analytics logic, integration decisions, and overall implementation direction are my own, and AI tools were used as a development assistant rather than a replacement for understanding the system.

## Why This Project Matters

Contest Analytics was built as a practical portfolio project around a real problem: making competitive programming progress easier to understand visually. It combines API integration, backend processing, database usage, frontend dashboards, and deployment into a single end-to-end application.

For recruiters or collaborators, this project demonstrates:

- full-stack project integration
- API design with FastAPI
- analytics-oriented Python backend development
- React dashboard design with reusable components
- deployment of a modern web application
- honest and responsible use of AI-assisted development

## Future Improvements

- Add caching for repeated handle lookups
- Add more advanced problem recommendations based on weak tags and rating history
- Add contest-by-contest performance trends
- Add authentication and saved user dashboards
- Improve test coverage for backend analytics routes and frontend data states