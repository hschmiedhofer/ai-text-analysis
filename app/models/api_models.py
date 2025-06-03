from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Annotated


class ErrorCategoryEnum(str, Enum):
    """Categories of text errors that can be detected."""

    SPELLING = "spelling"
    GRAMMAR = "grammar"
    STYLE = "style"


class ErrorDetail(BaseModel):
    """Individual error found in text with correction and metadata."""

    text_original: Annotated[str, Field(description="Original text with error")]
    text_corrected: Annotated[str, Field(description="Corrected version of text")]
    category: Annotated[ErrorCategoryEnum, Field(description="Type of error detected")]
    description: Annotated[
        str, Field(max_length=500, description="Brief explanation of the error")
    ]
    position: Annotated[
        int, Field(ge=0, description="Character position of error in text")
    ]
    context: Annotated[
        str, Field(max_length=200, description="Surrounding text context")
    ]


class ApiResponse(BaseModel):
    """Basic API response containing errors and summary."""

    errors: Annotated[list[ErrorDetail], Field(description="List of detected errors")]
    summary: Annotated[
        str, Field(max_length=1000, description="Overall assessment summary")
    ]


class TextAssessment(ApiResponse):
    """Extended assessment with original text and processing metadata."""

    text_submitted: Annotated[str, Field(description="Original text that was analyzed")]
    processing_time: Annotated[
        float, Field(ge=0, description="Processing time in seconds")
    ]
    tokens_used: Annotated[int, Field(ge=0, description="Number of tokens consumed")]
    created_at: Annotated[
        datetime, Field(description="Timestamp when assessment was created")
    ]
