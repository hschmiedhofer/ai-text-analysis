"""
Text Analysis Review Router

This module provides FastAPI endpoints for text analysis and review functionality.
It handles submission of text for AI-powered grammatical and stylistic analysis,
stores results in the database, and provides retrieval endpoints for assessments.

Endpoints:
    POST /review/           - Submit text for analysis
    GET /review/{id}        - Retrieve specific assessment by ID
    GET /review/            - List all assessments with pagination
"""

from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import select, desc
from ..services.security import verify_api_key
from ..models import ErrorDetailDB, TextAssessment, TextAssessmentDB
from ..services.text_analysis import identify_errors_in_text, GeminiGeneralError
from ..services.database import SessionDep
from ..services.converters import convert_db_to_response
from ..services.text_sanitizer import TextSanitizer

# configure /review endpoint router with API key authentication and common error responses
router = APIRouter(
    prefix="/review",
    tags=["Text Analysis"],
    dependencies=[Depends(verify_api_key)],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Authentication failed - invalid or missing API key",
            "content": {"application/json": {"example": {"detail": "Invalid API key"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "No authorization header provided",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)


# $ POST: /review
@router.post(
    "/",
    summary="Analyze text for errors",
    description="Submit text for grammatical and stylistic analysis using AI",
    response_description="Analysis results with identified errors and corrections",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Text analysis completed successfully"
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid input text"},
    },
)
async def analyze_text(
    article: Annotated[
        str,
        Body(
            title="Text to Analyze",
            description="The text content to analyze for grammatical and stylistic errors. Note: If your text contains double quotes, escape them with backslashes or use single quotes instead when possible.",
            example="Investing in robust media literacy educasion from an early age are not merely benefiscial, but, in point of fact, esential. It is required that we must equip citizen's with the critcal thinking skill's to evaluate sources.",
            min_length=1,
            max_length=50000,
        ),
    ],
    session: SessionDep,
) -> TextAssessment:
    """
    Analyze text for grammatical and stylistic errors using AI.

    This endpoint processes the submitted text through an AI language model
    to identify errors, provide corrections, and store the analysis results
    in the database for future retrieval.

    **Features:**
    - Identifies grammar, spelling, punctuation, and style errors
    - Provides specific corrections and explanations
    - Calculates precise error positions in the text
    - Stores results for historical tracking
    """
    # Input validation
    try:
        sanitized_article = TextSanitizer.sanitize(article)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid text content: {e}",
        )

    if not sanitized_article:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text cannot be empty or contain only whitespace",
        )

    # try to get assessment from LLM
    try:
        analysis_result = await identify_errors_in_text(sanitized_article)
    except GeminiGeneralError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text analysis service error: {e}",
        )

    # store assessment in database
    try:
        # store actual assessment
        assessment_db = TextAssessmentDB(
            text_submitted=analysis_result.text_submitted,
            summary=analysis_result.summary,
            tokens_used=analysis_result.tokens_used,
            processing_time=analysis_result.processing_time,
            created_at=analysis_result.created_at,
        )
        session.add(assessment_db)
        session.commit()
        session.refresh(assessment_db)  # Refresh to get the assigned ID

        # store dedicated individual errors
        for e in analysis_result.errors:
            curr_error = ErrorDetailDB(
                text_original=e.text_original,
                text_corrected=e.text_corrected,
                category=e.category,
                description=e.description,
                position=e.position,
                context=e.context,
                assessment_id=assessment_db.id,  # use id from committed assessment
            )
            session.add(curr_error)

        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while storing analysis results",
        )
    return analysis_result


# $ GET: /review/{assessment_id}
@router.get(
    "/{assessment_id}",
    summary="Retrieve specific assessment",
    description="Get detailed results of a previously completed text analysis",
    response_description="Complete assessment with all identified errors",
    responses={
        status.HTTP_200_OK: {"description": "Assessment retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Assessment not found"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid assessment ID format"
        },
    },
)
async def get_assessment(
    assessment_id: Annotated[
        int,
        Path(
            title="Assessment ID",
            description="Unique identifier of the text assessment to retrieve",
            example=123,
            ge=1,
        ),
    ],
    session: SessionDep,
) -> TextAssessment:
    """
    Retrieve a specific text assessment by its ID.

    Returns the complete analysis results including original text,
    AI-generated summary, processing metadata, and detailed error list.
    """

    statement = select(TextAssessmentDB).where(TextAssessmentDB.id == assessment_id)
    result = session.exec(statement)

    try:
        assessment_db = result.one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with ID {assessment_id} not found",
        )

    return convert_db_to_response(assessment_db)


# $ GET: /review
@router.get(
    "/",
    summary="List all assessments",
    description="Retrieve a list of all completed text analyses",
    response_description="List of assessments ordered by most recent first",
    responses={200: {"description": "Assessments retrieved successfully"}},
)
async def list_assessments(
    session: SessionDep,
    limit: Annotated[
        int,
        Query(
            title="Result Limit",
            description="Maximum number of assessments to return",
            example=50,
            ge=1,
            le=1000,
        ),
    ] = 100,
) -> list[TextAssessment]:
    """
    Retrieve all completed text assessments.

    Returns assessments ordered by creation date (most recent first).
    Useful for displaying analysis history or generating reports.

    **Query Parameters:**
    - limit: Maximum number of results (1-1000, default: 100)
    """

    statement = (
        select(TextAssessmentDB).order_by(desc(TextAssessmentDB.id)).limit(limit)
    )
    result = session.exec(statement)
    assessments_db = list(result.all())

    return [convert_db_to_response(assessment) for assessment in assessments_db]
