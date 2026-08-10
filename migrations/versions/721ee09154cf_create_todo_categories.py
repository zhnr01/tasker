"""create todo_categories

Revision ID: 721ee09154cf
Revises: 6b9294f79cd7
Create Date: 2026-08-10 10:27:49.043732

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "721ee09154cf"
down_revision: str | None = "d4adeec0c0d9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "todo_categories",
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
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("color", sa.Text()),
        sa.Column("description", sa.Text()),
    )
    op.create_index("idx_todo_categories_user_id", "todo_categories", ["user_id"])
    # THE business rule, enforced by the database: unique name per user.
    op.create_index(
        "uq_todo_categories_user_name",
        "todo_categories",
        ["user_id", "name"],
        unique=True,
    )
    op.execute(
        """
        CREATE TRIGGER set_updated_at_todo_categories
        BEFORE UPDATE ON todo_categories
        FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS set_updated_at_todo_categories ON todo_categories;"
    )
    op.drop_table("todo_categories")
