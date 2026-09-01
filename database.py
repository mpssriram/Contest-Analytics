import os
from pathlib import Path

import config as cfgq

cfg = cfgq.Config(Path(__file__).resolve().parent / "config.yaml")

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

MYSQL_HOST = cfg._get("database.host", "localhost")
MYSQL_PORT = cfg._get("database.port", 3306)
MYSQL_USER = cfg._get("database.user", "root")
MYSQL_PASSWORD = cfg._get("database.password", "")
MYSQL_DATABASE = cfg._get("database.database", "")

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

    import models

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
