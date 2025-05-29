from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, Query
from models.models import (
    ErrorCategoryEnum,
    ErrorDetail,
    ErrorDetailDB,
    TextAssessment,
    TextAssessmentDB,
)
from services.gemini import identify_errors_in_text, GeminiGeneralError
from http import HTTPStatus
from services.database import SessionDep
import json
from sqlmodel import select

router = APIRouter(
    prefix="/review", tags=["review"]
)  # todo add dependencies and responses


@router.post("/")
async def check_article(
    article: Annotated[str, Body()], session: SessionDep
) -> TextAssessment:

    try:
        returndata = identify_errors_in_text(article)
    except GeminiGeneralError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    # commit general assessment (yet without errors) to db to have an id
    a = TextAssessmentDB(
        summary=returndata.summary,
        tokens_used=returndata.tokens_used,
        processing_time=returndata.processing_time,
    )
    session.add(a)
    session.commit()

    for e in returndata.errors:
        curr_error = ErrorDetailDB(
            original_error_text=e.original_error_text,
            corrected_text=e.corrected_text,
            error_category=e.error_category,
            error_description=e.error_description,
            error_position=e.error_position,
            error_context=e.error_context,
            assessment_id=a.id,  # use id from committed assessment
        )
        session.add(curr_error)
        session.commit()

    session.refresh(a)  # what's the use of this?

    return returndata
