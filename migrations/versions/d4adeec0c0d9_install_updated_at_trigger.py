"""install updated_at trigger

Revision ID: d4adeec0c0d9
Revises:
Create Date: 2026-08-05 09:01:37.061599

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4adeec0c0d9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # A reusable trigger function: on any UPDATE, stamp updated_at = now().
    op.execute(
        """
        CREATE OR REPLACE FUNCTION trigger_set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION IF EXISTS trigger_set_updated_at();")
