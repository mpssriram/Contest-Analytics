# Entry point kept at the project root so `uvicorn app:app` (local and Railway) keeps working.
from backend.main import app  # noqa: F401
