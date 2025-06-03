from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime
from .api_models import ErrorCategoryEnum


class TextAssessmentDB(SQLModel, table=True):
    """Database model for storing text analysis assessments."""

    id: int | None = Field(default=None, primary_key=True)

    text_submitted: str
    processing_time: float
    summary: str
    tokens_used: int
    created_at: datetime

    errors: list["ErrorDetailDB"] = Relationship(back_populates="assessment")


class ErrorDetailDB(SQLModel, table=True):
    """Database model for storing individual text errors."""

    id: int | None = Field(default=None, primary_key=True)

    text_original: str
    text_corrected: str
    category: ErrorCategoryEnum
    description: str
    position: int
    context: str

    assessment_id: int | None = Field(default=None, foreign_key="textassessmentdb.id")
    assessment: TextAssessmentDB = Relationship(back_populates="errors")
