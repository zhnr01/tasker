"""change comments.user_id to UUID

Revision ID: 9d6e2d9e5f6b
Revises: 78f301cb43d0
Create Date: 2026-08-10 11:25:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "9d6e2d9e5f6b"
down_revision: str | None = "78f301cb43d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "comments",
        "user_id",
        existing_type=sa.Text(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        nullable=False,
        postgresql_using="CAST(user_id AS uuid)",
    )


def downgrade() -> None:
    op.alter_column(
        "comments",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Text(),
        existing_nullable=False,
        nullable=False,
        postgresql_using="CAST(user_id AS text)",
    )
