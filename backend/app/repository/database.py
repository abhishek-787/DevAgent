from app.memory.database import (
    Base,
    engine,
    get_session,
)


def initialize_database() -> None:
    from app.repository import (
        models as repository_models,
    )

    Base.metadata.create_all(
        bind=engine
    )