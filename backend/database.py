import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import Config

# config.yaml stays in the project root, one folder above backend/
cfg = Config(Path(__file__).resolve().parents[1] / "config.yaml")

MYSQL_HOST = cfg.get("database.host", "localhost")
MYSQL_PORT = cfg.get("database.port", 3306)
MYSQL_USER = cfg.get("database.user", "root")
MYSQL_PASSWORD = cfg.get("database.password", "")
MYSQL_DATABASE = cfg.get("database.database", "")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL and all(
    [MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE]
):
    DATABASE_URL = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    )

DB_CONFIGURED = bool(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True) if DB_CONFIGURED else None

SessionLocal = (
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    if DB_CONFIGURED
    else None
)

Base = declarative_base()


def get_db():
    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    if engine is None:
        return

    from backend import models  # registers the tables on Base

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
