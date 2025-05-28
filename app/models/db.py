from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str


class Assessment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text_original: str = Field(index=True)
    assessment: str = Field(index=True)
    tokens_used: int | None = Field(default=None)
    processing_time: float | None = Field(default=None)
