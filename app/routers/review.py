from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from ..services.security import verify_api_key
from ..models.models import ErrorDetail, ErrorDetailDB, TextAssessment, TextAssessmentDB
from ..services.llm_api import identify_errors_in_text, GeminiGeneralError
from http import HTTPStatus
from ..services.database import SessionDep
from sqlmodel import select

router = APIRouter(
    prefix="/review", tags=["review"], dependencies=[Depends(verify_api_key)]
)  # todo add dependencies and responses


# $ endpoint services
@router.post("/")
async def check_article(
    article: Annotated[str, Body()], session: SessionDep
) -> TextAssessment:

    try:
        returndata = await identify_errors_in_text(article)
    except GeminiGeneralError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    # commit general assessment (yet without errors) to db to have an id
    a = TextAssessmentDB(
        text_submitted=returndata.text_submitted,
        summary=returndata.summary,
        tokens_used=returndata.tokens_used,
        processing_time=returndata.processing_time,
    )
    session.add(a)
    session.commit()
    session.refresh(a)  # Refresh to get the assigned ID

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
    # session.refresh(a)  # what's the use of this?

    return returndata


@router.get("/{id}")
async def retrieve_assessment(id: int, session: SessionDep) -> TextAssessment:
    statement = select(TextAssessmentDB).where(TextAssessmentDB.id == id)
    result = session.exec(statement)
    review = result.one()

    return convert_db_to_response(review)


@router.get("/")
async def retrieve_assessment_all(session: SessionDep) -> list[TextAssessment]:
    statement = select(TextAssessmentDB)
    result = session.exec(statement)
    reviews = list(result.all())

    return [convert_db_to_response(review) for review in reviews]


# $ util functions
def convert_db_to_response(assessment_db: TextAssessmentDB) -> TextAssessment:
    """Convert TextAssessmentDB to TextAssessment response model."""
    error_details = [
        ErrorDetail(
            original_error_text=error.original_error_text,
            corrected_text=error.corrected_text,
            error_category=error.error_category,
            error_description=error.error_description,
            error_position=error.error_position,
            error_context=error.error_context,
        )
        for error in assessment_db.errors
    ]

    return TextAssessment(
        text_submitted=assessment_db.text_submitted,
        summary=assessment_db.summary,
        processing_time=assessment_db.processing_time,
        tokens_used=assessment_db.tokens_used,
        errors=error_details,
    )
