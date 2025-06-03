"""Database-to-API model conversion utilities."""

from ..models import ErrorDetail, TextAssessment, TextAssessmentDB


def convert_db_to_response(assessment_db: TextAssessmentDB) -> TextAssessment:
    """Convert TextAssessmentDB to TextAssessment response model.

    Transforms the database representation into the API response format,
    properly handling the relationship between assessments and their errors.

    Args:
        assessment_db: Database model containing assessment and related errors

    Returns:
        TextAssessment: API response model with all error details included
    """
    error_details = [
        ErrorDetail(
            text_original=error.text_original,
            text_corrected=error.text_corrected,
            category=error.category,
            description=error.description,
            position=error.position,
            context=error.context,
        )
        for error in assessment_db.errors
    ]

    return TextAssessment(
        text_submitted=assessment_db.text_submitted,
        summary=assessment_db.summary,
        processing_time=assessment_db.processing_time,
        tokens_used=assessment_db.tokens_used,
        errors=error_details,
        created_at=assessment_db.created_at,
    )
