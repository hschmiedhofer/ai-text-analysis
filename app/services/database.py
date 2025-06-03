"""
Database configuration and session management for the FastAPI application.

This module sets up SQLite database connection, creates database tables,
and provides dependency injection for database sessions.
"""

from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

# SQLite database configuration
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# SQLite connection arguments to allow multiple threads
connect_args = {"check_same_thread": False}

# Create database engine with SQLite connection
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    """
    Create database tables based on SQLModel metadata.

    This function should be called once during application startup
    to ensure all required tables exist in the database.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Create and yield a database session.

    This generator function creates a new database session,
    yields it for use, and automatically closes it when done.
    Used as a FastAPI dependency for database operations.

    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session


# Type alias for FastAPI dependency injection
# Provides a database session to route handlers automatically
SessionDep = Annotated[Session, Depends(get_session)]
