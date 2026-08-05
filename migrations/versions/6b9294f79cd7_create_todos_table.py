"""create todos table

Revision ID: 6b9294f79cd7
Revises: d4adeec0c0d9
Create Date: 2026-08-05 09:38:04.421712

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "6b9294f79cd7"
down_revision: Union[str, None] = "d4adeec0c0d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "todos",
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
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.Text(), nullable=False, server_default="draft"),
        sa.Column("priority", sa.Text(), nullable=False, server_default="medium"),
        sa.Column("due_date", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("parent_todo_id", postgresql.UUID(as_uuid=True)),
        sa.Column("category_id", postgresql.UUID(as_uuid=True)),
        sa.Column("metadata", postgresql.JSONB()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        # Self-reference for subtasks.
        sa.ForeignKeyConstraint(["parent_todo_id"], ["todos.id"]),
        # Deleting a category just un-categorizes its todos (SET NULL),
        # exactly like the Go schema.
        # sa.ForeignKeyConstraint(
        #     ["category_id"], ["todo_categories.id"], ondelete="SET NULL"
        # ),
    )
    # A todo can't be its own parent (matches the Go 'no_self_parent' constraint).
    op.create_check_constraint("no_self_parent", "todos", "id != parent_todo_id")

    # Indexes matching 002_todos.sql (query-driven, not guesswork).
    op.create_index("idx_todos_user_id", "todos", ["user_id"])
    op.create_index("idx_todos_category_id", "todos", ["category_id"])
    op.create_index("idx_todos_parent_todo_id", "todos", ["parent_todo_id"])
    op.create_index("idx_todos_status", "todos", ["status"])
    op.create_index("idx_todos_priority", "todos", ["priority"])
    op.create_index("idx_todos_due_date", "todos", ["due_date"])
    op.create_index("idx_todos_hierarchy", "todos", ["parent_todo_id", "sort_order"])
    op.create_index(
        "idx_todos_user_status_priority",
        "todos",
        ["user_id", "status", "priority"],
    )

    # Keep updated_at fresh via the trigger from Part 03.
    op.execute(
        """
        CREATE TRIGGER set_updated_at_todos
        BEFORE UPDATE ON todos
        FOR EACH ROW EXECUTE FUNCTION trigger_set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS set_updated_at_todos ON todos;")
    op.drop_table("todos")
