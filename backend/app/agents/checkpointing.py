import atexit
import sqlite3

from langgraph.checkpoint.sqlite import (
    SqliteSaver,
)

from app.memory.database import (
    DATA_DIR,
)


CHECKPOINT_PATH = (
    DATA_DIR
    / "checkpoints.db"
)


checkpoint_connection = (
    sqlite3.connect(
        str(CHECKPOINT_PATH),
        check_same_thread=False,
    )
)


checkpointer = SqliteSaver(
    checkpoint_connection
)


def close_checkpoint_connection() -> None:
    try:
        checkpoint_connection.close()
    except Exception:
        pass


atexit.register(
    close_checkpoint_connection
)