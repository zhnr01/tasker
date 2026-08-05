from enum import StrEnum


class TodoStatus(StrEnum):
    """Lifecycle of a todo. Mirrors the Go app's todo.Status.

    Note DRAFT — the Go app defaults new todos to 'draft', not 'active'.
    """

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TodoPriority(StrEnum):
    """Mirrors the Go app's todo.Priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
