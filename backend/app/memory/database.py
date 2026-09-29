import os
from pathlib import Path

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)


def get_devagent_data_dir() -> Path:
    appdata = os.getenv("APPDATA")

    if appdata:
        data_dir = (
            Path(appdata)
            / "DevAgent"
            / "data"
        )
    else:
        data_dir = (
            Path.home()
            / ".devagent"
            / "data"
        )

    data_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return data_dir


DATA_DIR = get_devagent_data_dir()

DATABASE_PATH = (
    DATA_DIR
    / "devagent.db"
)

DATABASE_URL = (
    f"sqlite:///"
    f"{DATABASE_PATH.as_posix()}"
)


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)


class Base(
    DeclarativeBase
):
    pass


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_session():
    return SessionLocal()


def initialize_memory_database() -> None:
    from app.memory import (
        models as memory_models,
    )

    Base.metadata.create_all(
        bind=engine
    )