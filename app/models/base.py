import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Timezone-aware UTC now. Always store UTC; convert at the edges only."""
    return datetime.now(UTC)


class BaseModel(SQLModel):
    """Common columns for every table (mirrors the Go app's model.Base).

    Not a table itself — it's a mixin. Concrete tables inherit these so `id` and
    the timestamps are declared in exactly one place.
    """

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Server-generated UUID primary key.",
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
        index=True,  # we sort/paginate by created_at, so index it
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        nullable=False,
    )
