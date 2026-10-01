from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import compare, problems, profile, tracked_handles
from backend.database import create_tables
from backend.services.codeforces_client import CodeforcesAPIError, InvalidHandleError

logger = logging.getLogger("contest_analytics")

FRONTEND_URL = os.getenv("FRONTEND_URL")

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://contest-analytics.vercel.app",
    "https://contest-analytics-m822fntiv-mpssrirams-projects.vercel.app",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        create_tables()
    except Exception:
        logger.exception("Startup warning: could not create tables")
    yield


app = FastAPI(title="Contest Analytics API", version="1.0.0", lifespan=lifespan)


@app.exception_handler(CodeforcesAPIError)
async def codeforces_error_handler(_request: Request, error: CodeforcesAPIError) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": error.message})


@app.exception_handler(InvalidHandleError)
async def invalid_handle_handler(_request: Request, error: InvalidHandleError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(error)})


# Registered before CORSMiddleware so CORS wraps it and 500s still carry CORS
# headers; otherwise the browser reports a CORS failure instead of the error.
@app.middleware("http")
async def unexpected_error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(status_code=500, content={"detail": "Unexpected server error."})


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://contest-analytics.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def root_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/health", tags=["Contest Analytics"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "contest-analytics-api"}


app.include_router(tracked_handles.router)
app.include_router(profile.router)
app.include_router(problems.router)
app.include_router(compare.router)
