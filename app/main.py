from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError
from .services.text_analysis import GeminiGeneralError
from .services.database import create_db_and_tables
from .routers import review


# lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    yield
    # Shutdown


# create fastapi app
app = FastAPI(lifespan=lifespan)


# add custom exception handlers to app
@app.exception_handler(GeminiGeneralError)
async def gemini_exception_handler(request: Request, exc: GeminiGeneralError):
    """Exception handler for LLM errors."""
    return JSONResponse(
        status_code=500, content={"detail": f"AI service error: {str(exc)}"}
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Exception handler for DB errors."""
    logging.error(f"Database error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"detail": "Database operation failed"}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    logging.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# add endpoint router(s) to app
app.include_router(review.router)
