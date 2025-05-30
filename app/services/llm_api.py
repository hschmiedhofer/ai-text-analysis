import os
import time
from ..models.models import ApiResponse, ErrorDetail, TextAssessment
from pydantic_ai import Agent
import logfire
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from .env file

# Get the API key from environment variable
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No GOOGLE_API_KEY found in environment variables.")

# Get the model ID from environment variable
GEMINI_MODEL_ID = os.getenv("MODEL_ID")
if not GEMINI_MODEL_ID:
    raise ValueError("No MODEL_ID found in environment variables.")


# custom exception (optional, but good practice)
class GeminiGeneralError(Exception):
    pass


# TODO do we need this?
# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()

# create model communication agent
# TODO use gemini key
agent = Agent(GEMINI_MODEL_ID, output_type=ApiResponse)


async def identify_errors_in_text(text: str) -> TextAssessment:
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
        # re-raise as a custom error for specific handling upstream
        raise GeminiGeneralError(f"API call failed: {e}")

    # validate api response
    if not (
        agent_response
        and agent_response.output
        and isinstance(agent_response.output, ApiResponse)
    ):
        raise GeminiGeneralError(f"Invalid response from API.")

    assessment = TextAssessment(
        text_submitted=text,
        summary=agent_response.output.summary,
        processing_time=processing_time,
        tokens_used=agent_response.usage().total_tokens or 0,
        errors=agent_response.output.errors,
    )

    # validate the resulting error locations and drop incorrectly described errors
    validate_assessment(text, assessment)

    return assessment


def validate_assessment(text_orig: str, assessment: TextAssessment) -> None:
    errors_validated: list[ErrorDetail] = []
    for e in assessment.errors:
        try:
            # location of error in context
            idx_error_in_context = e.error_context.index(e.original_error_text)
            # location of context in original text
            idx_context_in_orig = text_orig.index(e.error_context)
            # final location
            idx = idx_error_in_context + idx_context_in_orig
            print(f"actual location: {idx} / suggested location: {e.error_position}")
            # correct index and store
            e.error_position = idx
            errors_validated.append(e)
        except ValueError:
            print(f"dropped incorrectly specified error: {e}")

    assessment.errors = errors_validated


async def test():
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
