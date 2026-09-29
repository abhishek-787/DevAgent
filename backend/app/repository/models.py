from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    JSON,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.repository.database import (
    Base,
)


class RepositoryChunk(Base):
    __tablename__ = (
        "repository_chunks"
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_path",
            "file_path",
            "start_line",
            "end_line",
            name=(
                "uq_repository_chunk"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    workspace_path: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    file_path: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    language: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    chunk_type: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    symbol_name: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    start_line: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
        )
    )

    end_line: Mapped[int] = (
        mapped_column(
            Integer,
            nullable=False,
        )
    )

    content: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    content_hash: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    embedding: Mapped[
        list[float] | None
    ] = mapped_column(
        JSON(
            none_as_null=True
        ),
        nullable=True,
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )