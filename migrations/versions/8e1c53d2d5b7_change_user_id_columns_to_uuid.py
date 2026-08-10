"""change user_id columns to UUID

Revision ID: 8e1c53d2d5b7
Revises: 6b9294f79cd7
Create Date: 2026-08-10 10:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8e1c53d2d5b7"
down_revision: str | None = "6b9294f79cd7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "todo_categories",
        "user_id",
        existing_type=sa.Text(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        nullable=False,
        postgresql_using="CAST(user_id AS uuid)",
    )
    op.alter_column(
        "todos",
        "user_id",
        existing_type=sa.Text(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        nullable=False,
        postgresql_using="CAST(user_id AS uuid)",
    )


def downgrade() -> None:
    op.alter_column(
        "todo_categories",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Text(),
        existing_nullable=False,
        nullable=False,
        postgresql_using="CAST(user_id AS text)",
    )
    op.alter_column(
        "todos",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Text(),
        existing_nullable=False,
        nullable=False,
        postgresql_using="CAST(user_id AS text)",
    )
