import atexit

import psycopg

from langgraph.checkpoint.postgres import (
    PostgresSaver,
)
from psycopg.rows import (
    dict_row,
)

from app.core.config import (
    settings,
)


def _get_checkpoint_database_url() -> str:
    database_url = (
        settings.database_url
    )

    return database_url.replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )


checkpoint_connection = (
    psycopg.connect(
        _get_checkpoint_database_url(),
        autocommit=True,
        prepare_threshold=0,
        row_factory=dict_row,
    )
)


checkpointer = PostgresSaver(
    checkpoint_connection
)


checkpointer.setup()


def close_checkpoint_connection() -> None:
    if not checkpoint_connection.closed:
        checkpoint_connection.close()


atexit.register(
    close_checkpoint_connection
)