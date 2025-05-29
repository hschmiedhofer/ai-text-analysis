from typing import Literal
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum


class ErrorCategoryEnum(str, Enum):
    SPELLING = "spelling"
    GRAMMAR = "grammar"
    STYLE = "style"


class ErrorDetail(SQLModel):
    original_error_text: str
    corrected_text: str
    error_category: ErrorCategoryEnum  # Use Enum instead of Literal
    error_description: str
    error_position: int
    error_context: str


# expected response from the api
class ApiResponse(SQLModel):
    errors: list[ErrorDetail]
    summary: str


# api response enhanced with api request metadata.
class TextAssessment(ApiResponse):
    processing_time: float
    tokens_used: int


class TextAssessmentDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    processing_time: float = Field()
    summary: str = Field()
    tokens_used: int = Field()

    errors: list["ErrorDetailDB"] = Relationship(back_populates="assessment")


class ErrorDetailDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    original_error_text: str
    corrected_text: str
    error_category: ErrorCategoryEnum
    error_description: str
    error_position: int
    error_context: str

    assessment_id: int | None = Field(default=None, foreign_key="textassessmentdb.id")
    assessment: TextAssessmentDB = Relationship(back_populates="errors")
