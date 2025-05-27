from typing import Annotated
from fastapi import APIRouter, Body, HTTPException
from models.models import TextAssessment
from services.gemini import identify_errors_in_text, GeminiGeneralError
from http import HTTPStatus

router = APIRouter(
    prefix="/review", tags=["review"]
)  # todo add dependencies and responses


@router.post("/")
async def check_article(article: Annotated[str, Body()]) -> TextAssessment:

    try:
        returndata = identify_errors_in_text(article)
    except GeminiGeneralError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    return returndata
