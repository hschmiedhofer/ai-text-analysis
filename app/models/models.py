from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, Relationship, SQLModel
from enum import Enum


class ErrorCategoryEnum(str, Enum):
    SPELLING = "spelling"
    GRAMMAR = "grammar"
    STYLE = "style"


class ErrorDetail(SQLModel):
    original_error_text: str
    corrected_text: str
    error_category: ErrorCategoryEnum
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
    processing_time: float
    summary: str
    tokens_used: int

    errors: list["ErrorDetailDB"] = Relationship(back_populates="assessment")


class ErrorDetailDB(ErrorDetail, table=True):
    id: int | None = Field(default=None, primary_key=True)

    assessment_id: int | None = Field(default=None, foreign_key="textassessmentdb.id")
    assessment: TextAssessmentDB = Relationship(back_populates="errors")
