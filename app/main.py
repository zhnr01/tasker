from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.api.router import api_router
from app.api.routes import health
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hook.

    Code before `yield` runs once at startup; code after runs at shutdown. Right
    now there's nothing to set up — in later parts we'll create the DB engine
    here (Part 03) and drain connections on shutdown (Part 23).
    """
    # --- startup ---
    yield
    # --- shutdown ---


def create_app() -> FastAPI:
    """Application factory: build, wire, and return the FastAPI app.

    Everything the app needs (routers, middleware, error handlers) gets attached
    here, so there's exactly one place that describes the whole application.
    """
    settings = get_settings()  # built & validated once, here at startup
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        summary="A production-grade Todo API, rebuilt from the Go tasker.",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Register route groups. As the app grows, new APIRouters get included here
    # (Part 05 introduces the /v1 aggregator that bundles them all).
    app.include_router(health.router)
    # Everything else lives under /v1.
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


# Uvicorn imports this module-level `app`. Keeping it as a thin call to the
# factory means production and tests build the app the exact same way.
app = create_app()
