import os
import time
from datetime import datetime, timezone
from pydantic_ai import Agent, AgentRunError
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
    raise ValueError("No MODEL_ID found in environment variables.")


# custom exception (optional, but good practice)
class GeminiGeneralError(Exception):
    pass


# create model communication agent
model = GeminiModel(GEMINI_MODEL_ID, provider=GoogleGLAProvider(api_key=GEMINI_API_KEY))
agent = Agent(model, output_type=ApiResponse)


async def identify_errors_in_text(text: str) -> TextAssessment:
    """Analyze text for spelling, grammar, and style errors using Gemini AI.

    Args:
        text: The text to analyze for errors.

    Returns:
        TextAssessment containing detected errors, summary, and metadata.

    Raises:
        GeminiGeneralError: If API call fails or returns invalid response.
    """
    prompt = """
        You are an expert proof-reader. I gave you an article. I want you to scan it for errors.

        For each error you found, supply the following information:
        - original error text
        - corrected error text
        - category of the error
        - location of the first character of the original error text. Character indexes start at 0.
        - verbatim description of the error
        - context. here, give me the original error plus some leading and trailing characters.In total, this text must be a subset of the supplied article.

        With regard to the entire article, give me:
        - a summary of the text quality.
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
        else:
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
    """Validate and correct error positions in assessment, removing invalid errors.

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


async def test():
    """Test function that analyzes a faulty article and exports results to JSON."""
    # read article from test data
    faulty_article = ""
    article_file_path = "testdata/faulty_article.txt"
    try:
        with open(article_file_path, "r") as f:
            faulty_article = f.read()
    except Exception as e:
        print(f"Error reading file '{article_file_path}': {e}")
        exit(1)

    # query the api for the correction
    api_assessment = await identify_errors_in_text(faulty_article)

    # write result to file
    output_file_path = "logs/identified_errors.json"
    try:
        with open(output_file_path, "w") as f:
            f.write(api_assessment.model_dump_json(indent=2))
        print(f"Successfully exported errors to {output_file_path}")
    except IOError as e:
        print(f"Failed to write errors to JSON file: {e}")
        exit(1)


#  make the script executable for testing
if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
