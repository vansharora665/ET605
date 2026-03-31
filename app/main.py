from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import RedirectResponse

from app.api.routes.demo import router as demo_router
from app.api.routes.merge import router as merge_router
from app.core.config import get_settings
from app.core.errors import ApiError
from app.core.logging import configure_logging
from app.db.session import init_db
from app.web.explainer_page import render_explainer_page
from app.web.demo_page import render_demo_page

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("Database initialized")
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Central Merge System for adaptive mathematics modules. "
            "Receives session-end interactions, computes performance scores, "
            "and recommends prerequisite chapters for struggling learners."
        ),
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    @app.exception_handler(ApiError)
    async def api_error_handler(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Payload validation failed",
                "errors": jsonable_encoder(exc.errors()),
            },
        )

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def root() -> str:
        return render_demo_page()

    @app.get("/open-docs", include_in_schema=False)
    def open_docs() -> RedirectResponse:
        return RedirectResponse(url=settings.docs_url, status_code=307)

    @app.get("/engine-explainer", response_class=HTMLResponse, include_in_schema=False)
    def engine_explainer() -> str:
        return render_explainer_page()

    app.include_router(demo_router)
    app.include_router(merge_router)
    return app


app = create_app()
