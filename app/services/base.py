from sqlmodel import Session


class BaseService:
    """Base for services. Holds the request-scoped session so a service can
    construct the repositories it needs. Business rules live in subclasses."""

    def __init__(self, session: Session) -> None:
        self.session = session
