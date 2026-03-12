"""create request comments"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260312_0010"
down_revision: str | None = "20260312_0009"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "request_comments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("request_id", sa.UUID(), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("membership_id", sa.UUID(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["membership_id"], ["organization_memberships.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_request_comments_request_created_at",
        "request_comments",
        ["request_id", "created_at"],
        unique=False,
    )
    op.execute(
        "ALTER TYPE request_activity_type "
        "ADD VALUE IF NOT EXISTS 'REQUEST_COMMENT_ADDED'"
    )


def downgrade() -> None:
    op.drop_index("ix_request_comments_request_created_at", table_name="request_comments")
    op.drop_table("request_comments")
    op.execute(
        "DELETE FROM request_activities "
        "WHERE type = 'REQUEST_COMMENT_ADDED'"
    )
    op.execute("ALTER TYPE request_activity_type RENAME TO request_activity_type_old")
    op.execute(
        "CREATE TYPE request_activity_type AS ENUM ("
        "'REQUEST_CREATED', "
        "'STATUS_CHANGED', "
        "'COMMENT_ADDED', "
        "'DOCUMENT_UPLOADED', "
        "'DOCUMENT_VERIFIED_DATA_UPDATED', "
        "'NOTE_ADDED'"
        ")"
    )
    op.execute(
        "ALTER TABLE request_activities "
        "ALTER COLUMN type TYPE request_activity_type "
        "USING type::text::request_activity_type"
    )
    op.execute("DROP TYPE request_activity_type_old")

