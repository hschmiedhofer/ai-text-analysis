from fastapi import FastAPI, Request
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.exc import SQLAlchemyError
from .services.text_analysis import GeminiGeneralError
from .services.database import create_db_and_tables
from .routers import review
from fastapi.responses import HTMLResponse

# create fastapi app
app = FastAPI()

# add custom exception handlers


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


# create DB on application startup
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# add endpoint router(s)
app.include_router(review.router)
