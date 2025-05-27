from typing import Literal
from pydantic import BaseModel


class Editorial(BaseModel):
    name: str
    text: str


class ErrorDetail(BaseModel):
    original_error_text: str
    corrected_text: str
    error_category: Literal["spelling", "grammar"]


class ListOfErrors(BaseModel):
    errors: list[ErrorDetail]
