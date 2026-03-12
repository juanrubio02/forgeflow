from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class RequestCommentModel(Base):
    __tablename__ = "request_comments"
    __table_args__ = (
        Index("ix_request_comments_request_created_at", "request_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    request_id: Mapped[UUID] = mapped_column(
        ForeignKey("requests.id", ondelete="RESTRICT"),
        nullable=False,
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    membership_id: Mapped[UUID] = mapped_column(
        ForeignKey("organization_memberships.id", ondelete="RESTRICT"),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

