from datetime import datetime

from sqlalchemy import (
    BigInteger,
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


class WorkspaceMemory(Base):
    __tablename__ = (
        "workspace_memories"
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_path",
            "memory_key",
            name="uq_workspace_memory",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    workspace_path: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    memory_key: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    memory_value: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
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


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    thread_id: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        index=True,
    )

    workspace_path: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
            index=True,
        )
    )

    user_message: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    answer: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    tools_used: Mapped[
        list[str]
    ] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    tool_rounds: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            nullable=False,
        )
    )

    failed_test_runs: Mapped[int] = (
        mapped_column(
            Integer,
            default=0,
            nullable=False,
        )
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


class AgentAuditEvent(Base):
    __tablename__ = (
        "agent_audit_events"
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    thread_id: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
            index=True,
        )
    )

    workspace_path: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
            index=True,
        )
    )

    event_type: Mapped[str] = (
        mapped_column(
            Text,
            nullable=False,
        )
    )

    details: Mapped[dict] = (
        mapped_column(
            JSON,
            default=dict,
            nullable=False,
        )
    )

    created_at: Mapped[
        datetime
    ] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )