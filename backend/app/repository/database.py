from sqlalchemy import (
    create_engine,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

from app.core.config import (
    settings,
)


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
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


def initialize_database() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE EXTENSION IF NOT EXISTS vector;
                """
            )
        )

    from app.repository import (
        models as repository_models,
    )

    from app.memory import (
        models as memory_models,
    )

    Base.metadata.create_all(
        bind=engine
    )