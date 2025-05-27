import os
import pathlib
import time
from typing import Any, Literal
from dotenv import load_dotenv
from google import genai
from google.genai import errors as api_exceptions
from pydantic import BaseModel


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


# *----------------


# custom exception (optional, but good practice)
class GeminiGeneralError(Exception):
    pass


class ErrorDetail(BaseModel):
    original_error_text: str
    corrected_text: str
    error_category: Literal["spelling", "grammar", "style"]
    error_description: str
    error_position: int
    error_context: str


# expected response from the api
class ApiResponse(BaseModel):
    errors: list[ErrorDetail]
    summary: str


# api response enhanced with api request metadata.
class TextAssessment(ApiResponse):
    processing_time: float
    tokens_used: int


def identify_errors_in_text(
    text: str,
) -> tuple[ApiResponse, dict[str, Any]]:
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
        raise GeminiGeneralError(f"API call failed: {e}") from e

    # Collect metadata
    metadata = {
        "processing_time": processing_time,
        "prompt_tokens": None,
        "response_tokens": None,
        "total_tokens": None,
    }

    # Access usage metadata
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage = response.usage_metadata
        metadata.update(
            {
                "prompt_tokens": usage.prompt_token_count,
                "response_tokens": usage.candidates_token_count,
                "total_tokens": usage.total_token_count,
            }
        )

    return (response.parsed, metadata)


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
    api_response, api_metadata = identify_errors_in_text(faulty_article)

    final = TextAssessment(
        errors=api_response.errors,
        summary=api_response.summary,
        processing_time=api_metadata["processing_time"],
        tokens_used=api_metadata["total_tokens"] or 0,  # Use 0 if None
    )

    # write result to file
    output_file_path = "logs/identified_errors.json"
    try:
        with open(output_file_path, "w") as f:
            f.write(final.model_dump_json(indent=2))
        print(f"Successfully exported errors to {output_file_path}")
    except IOError as e:
        print(f"Failed to write errors to JSON file: {e}")
        exit(1)
