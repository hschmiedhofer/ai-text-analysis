import os
import time
from enum import Enum
from dotenv import load_dotenv
from google import genai
from google.genai import errors as api_exceptions
from models.models import ApiResponse, ErrorDetail, TextAssessment

# from models.models import TextAssessment, ApiResponse


load_dotenv()  # Load environment variables from .env file

# Get the API key from environment variable
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No GOOGLE_API_KEY found in environment variables.")

# Get the model ID from environment variable
GEMINI_MODEL_ID = os.getenv("MODEL_ID")
if not GEMINI_MODEL_ID:
    raise ValueError("No MODEL_ID found in environment variables.")

# create gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


# custom exception (optional, but good practice)
class GeminiGeneralError(Exception):
    pass


def identify_errors_in_text(
    text: str,
) -> TextAssessment:
    assert GEMINI_MODEL_ID is not None

    prompt = """
            You are an expert proof-reader. Find errors in the following document. 
            For each error, include error_context that starts with the original_error_text 
            and adds the following 50 characters from the original text. 
            Do not add characters that came before the original_error_text!!
            Additionally, return your summary of the text quality.
    """

    try:
        start_time = time.time()
        response = client.models.generate_content(
            model=GEMINI_MODEL_ID,
            contents=[prompt, text],
            config={
                "response_mime_type": "application/json",
                "response_schema": ApiResponse,
            },
        )
        end_time = time.time()
        processing_time = end_time - start_time
    except api_exceptions.APIError as e:
        # re-raise as a custom error for specific handling upstream
        raise GeminiGeneralError(f"API call failed: {e}")

    # parse response to expected model
    if isinstance(response.parsed, ApiResponse):
        response_model = response.parsed
    else:
        raise GeminiGeneralError(f"Invalid response type: {type(response.parsed)}")

    # check for response metadata.
    if not (hasattr(response, "usage_metadata") and response.usage_metadata):
        raise GeminiGeneralError(f"Response is missing metadata.")

    assessment = TextAssessment(
        errors=response_model.errors,
        summary=response_model.summary,
        processing_time=processing_time,
        tokens_used=response.usage_metadata.total_token_count or 0,  # Use 0 if None
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


#  make the script executable for testing
if __name__ == "__main__":

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
    api_assessment = identify_errors_in_text(faulty_article)

    # validate the resulting error locations and drop incorrectly described errors
    validate_assessment(faulty_article, api_assessment)

    # write result to file
    output_file_path = "logs/identified_errors.json"
    try:
        with open(output_file_path, "w") as f:
            f.write(api_assessment.model_dump_json(indent=2))
        print(f"Successfully exported errors to {output_file_path}")
    except IOError as e:
        print(f"Failed to write errors to JSON file: {e}")
        exit(1)
