from typing import Annotated
from fastapi import APIRouter, Body, HTTPException, Query
from models.models import TextAssessment, TextAssessmentDB
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

    errors = returndata.errors
    errors_json = json.dumps([error.model_dump() for error in errors])
    test = TextAssessmentDB(
        summary=returndata.summary,
        processing_time=returndata.processing_time,
        tokens_used=returndata.tokens_used,
        errors=errors_json,
    )
    session.add(test)
    session.commit()
    session.refresh(test)

    return returndata


@router.get("/")
def read_entries(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[TextAssessmentDB]:
    entries = session.exec(select(TextAssessmentDB).offset(offset).limit(limit)).all()
    entries = list(entries)
    return entries
