"""
Text Analysis Service using Google Gemini AI

Provides AI-powered text analysis to identify grammatical, spelling, and
stylistic errors. Handles API communication, validates error positions,
and returns structured assessment results.

Main function: identify_errors_in_text() - analyzes text and returns TextAssessment
Custom exception: GeminiGeneralError - for API-related failures

Requires GOOGLE_API_KEY and GEMINI_MODEL_ID environment variables.
"""

import os
import time
from datetime import datetime, timezone
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider
from dotenv import load_dotenv
import logging
from ..models import ApiResponse, ErrorDetail, TextAssessment

logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

# Get the API key from environment variable
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No GOOGLE_API_KEY found in environment variables.")

# Get the model ID from environment variable
GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID")
if not GEMINI_MODEL_ID:
    raise ValueError("No GEMINI_MODEL_ID found in environment variables.")


# custom exception (optional, but good practice)
class GeminiGeneralError(Exception):
    pass


# create model communication agent
model = GeminiModel(GEMINI_MODEL_ID, provider=GoogleGLAProvider(api_key=GEMINI_API_KEY))
agent = Agent(model, output_type=ApiResponse)


async def identify_errors_in_text(text: str) -> TextAssessment:
    """
    Analyze text for spelling, grammar, and style errors using Gemini AI.

    Args:
        text: The text to analyze for errors.

    Returns:
        TextAssessment containing detected errors, summary, and metadata.

    Raises:
        GeminiGeneralError: If API call fails or returns invalid response.
    """

    prompt = """
    You are an expert proofreader and copy editor. Analyze the provided text for errors and provide a structured assessment.

    TASK: Identify text errors and provide an overall quality summary.

    ERROR DETECTION RULES:
    - Focus on genuine errors, not subjective style preferences
    - Categorize each error as: "spelling", "grammar", or "style"
    - Provide precise character positions (0-based indexing)
    - Include sufficient context to locate errors accurately
    - Limit to maximum 30 errors to ensure quality over quantity

    FOR EACH ERROR, provide exactly:
    - text_original: The exact erroneous text as it appears. Return the wrong word only, not the entire sentence.
    - text_corrected: Your suggested correction.
    - category: Must be one of: "spelling", "grammar", "style"
    - description: Brief explanation (under 500 characters)
    - position: 0-based character index where error starts
    - context: The exact erroneous text along with leading and trailing characters. 200 characters in total. Must contain the original text and must be an exact substring of the original text.

    CATEGORY DEFINITIONS:
    - spelling: Misspelled words, typos, incorrect word forms
    - grammar: Subject-verb agreement, tense errors, sentence structure, punctuation
    - style: Awkward phrasing, word choice, clarity issues, redundancy

    QUALITY SUMMARY:
    Provide an overall assessment (under 1000 characters) covering:
    - General readability and clarity
    - Most frequent error types found
    - Text quality rating (poor/fair/good/excellent)
    - Key recommendations for improvement

    CRITICAL: Ensure all character positions and contexts are precisely accurate. The context must be an exact substring that exists in the original text.

    RESPONSE FORMAT: Provide a structured response with "errors" array and "summary" string as specified.
    """

    try:
        start_time = time.time()
        agent_response = await agent.run([prompt, text])
        end_time = time.time()
        processing_time = end_time - start_time
    except Exception as e:
        # categorize  error based on exception content
        error_str = str(e).lower()
        if "rate limit" in error_str or "quota" in error_str:
            reason = "rate_limit_exceeded"
        elif "timeout" in error_str:
            reason = "request_timeout"
        elif "authentication" in error_str or "unauthorized" in error_str:
            reason = "authentication_failed"
        elif "network" in error_str or "connection" in error_str:
            reason = "network_error"
        elif "invalid" in error_str and "key" in error_str:
            reason = "invalid_api_key"
        elif "overloaded" in error_str or "unavailable" in error_str:
            reason = "model_overloaded"
        else:
            logger.error(f"\nLLM API Error: {str(e)}")
            reason = "unknown_api_error"
        # re-raise as a custom error for specific handling upstream
        raise GeminiGeneralError(f"API call failed ({reason})")

    # validate api response
    if not isinstance(agent_response.output, ApiResponse):
        raise GeminiGeneralError(f"Invalid response from API.")

    # safe token usage extraction
    try:
        tokens_used = agent_response.usage().total_tokens or 0
    except (AttributeError, TypeError):
        tokens_used = 0

    assessment = TextAssessment(
        text_submitted=text,
        summary=agent_response.output.summary,
        processing_time=processing_time,
        tokens_used=tokens_used,
        errors=agent_response.output.errors,
        created_at=datetime.now(timezone.utc),
    )

    # validate the resulting error locations and drop incorrectly described errors
    validate_assessment(text, assessment)

    return assessment


def validate_assessment(text_orig: str, assessment: TextAssessment) -> None:
    """
    Validate and correct error positions in assessment, removing invalid errors.

    Args:
        text_orig: Original text that was analyzed.
        assessment: Assessment object to validate and modify in-place.
    """

    errors_validated: list[ErrorDetail] = []
    for e in assessment.errors:
        try:
            # location of error in context
            idx_error_in_context = e.context.index(e.text_original)

            # Find all possible context locations
            context_positions = []
            start = 0
            while True:
                pos = text_orig.find(e.context, start)
                if pos == -1:
                    break
                context_positions.append(pos)
                start = pos + 1

            if not context_positions:
                raise ValueError("Context not found in original text")

            # Find the correct context position by checking which one gives valid error position
            valid_position = None
            for context_pos in context_positions:
                calculated_pos = idx_error_in_context + context_pos
                # Validate the position actually contains the error text
                if (
                    calculated_pos + len(e.text_original) <= len(text_orig)
                    and text_orig[
                        calculated_pos : calculated_pos + len(e.text_original)
                    ]
                    == e.text_original
                ):
                    valid_position = calculated_pos
                    break

            if valid_position is None:
                raise ValueError("No valid position found for error")

            logger.debug(
                f"\nactual location: {valid_position} / suggested location: {e.position}"
            )
            e.position = valid_position
            errors_validated.append(e)

        except ValueError as ve:
            logger.warning(f"\ndropped incorrectly specified error: {e} - Reason: {ve}")

    assessment.errors = errors_validated
