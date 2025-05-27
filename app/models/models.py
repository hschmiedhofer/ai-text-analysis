from typing import Literal
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    original_error_text: str
    corrected_text: str
    error_category: Literal["spelling", "grammar", "style"]
    error_description: str
    error_position: int
    error_context: str


# expected response from the api
class ApiResponse(BaseModel):
    errors: list[ErrorDetail]
    summary: str


# api response enhanced with api request metadata.
class TextAssessment(ApiResponse):
    processing_time: float
    tokens_used: int
