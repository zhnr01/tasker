"""create comments

Revision ID: 78f301cb43d0
Revises: 8e1c53d2d5b7
Create Date: 2026-08-10 11:14:29.224514

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "78f301cb43d0"
down_revision: str | None = "8e1c53d2d5b7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        # CASCADE: comments are meaningless without their todo, so delete them
        # automatically when the todo goes.
        sa.Column("todo_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["todo_id"], ["todos.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_comments_todo_id", "comments", ["todo_id"])
    op.execute(
        """
        CREATE TRIGGER set_updated_at_comments
        BEFORE UPDATE ON comments
        FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_comments ON comments;")
    op.drop_table("comments")
