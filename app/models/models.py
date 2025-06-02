from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum
from datetime import datetime, timezone
from typing import Annotated


class ErrorCategoryEnum(str, Enum):
    SPELLING = "spelling"
    GRAMMAR = "grammar"
    STYLE = "style"


# $ API models


class ErrorDetail(BaseModel):
    text_original: str
    text_corrected: str
    category: ErrorCategoryEnum
    description: str
    position: int
    context: str


# expected response from the api
class ApiResponse(BaseModel):
    errors: list[ErrorDetail]
    summary: str


# api response enhanced with api request metadata.
class TextAssessment(ApiResponse):
    text_submitted: str
    processing_time: float
    tokens_used: int
    created_at: datetime


# $ DB models


class TextAssessmentDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    text_submitted: str
    processing_time: float
    summary: str
    tokens_used: int
    created_at: datetime

    errors: list["ErrorDetailDB"] = Relationship(back_populates="assessment")


class ErrorDetailDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    text_original: str
    text_corrected: str
    category: ErrorCategoryEnum
    description: str
    position: int
    context: str

    assessment_id: int | None = Field(default=None, foreign_key="textassessmentdb.id")
    assessment: TextAssessmentDB = Relationship(back_populates="errors")
