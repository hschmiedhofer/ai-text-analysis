import pathlib
import os
from typing import Literal
from dotenv import load_dotenv
from google import genai
from google.genai import types, Client
from google.genai.chats import Chat
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, File
from google.genai import errors as api_exceptions
from pydantic import BaseModel


import logging


# TODO check if folder exists
logger_level = logging.ERROR
logger_file = "logs/logs.log"
logger_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(level=logger_level)
try:
    file_handler = logging.FileHandler(logger_file)
    file_handler.setLevel(logging.DEBUG)  # Log DEBUG and above to file
    file_handler.setFormatter(logger_formatter)
    logger.addHandler(file_handler)
except PermissionError:
    logger.error("Could not open log file due to permissions.")


load_dotenv()  # Load environment variables from .env file

# Get the API key from environment variable
# TODO would this be something for the __init__.py file?
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No GOOGLE_API_KEY found in environment variables.")

# Get the model ID from environment variable
GEMINI_MODEL_ID = os.getenv("MODEL_ID")
if not GEMINI_MODEL_ID:
    raise ValueError("No MODEL_ID found in environment variables.")

# create gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


# Define a custom exception (optional, but good practice)
class SummarizationError(Exception):
    pass


def summarize_text(text_to_summarize: str, addt_prompt="Summarize this text"):
    assert GEMINI_MODEL_ID is not None

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_ID, contents=[addt_prompt, text_to_summarize]
        )
    except api_exceptions.APIError as e:
        logger.error(
            f"Gemini API call failed during text summarization: {e}", exc_info=True
        )
        # Option 1: Re-raise as a custom error for specific handling upstream
        raise SummarizationError(f"API call failed: {e}") from e

    # --- If the API call succeeded, proceed to check the response ---
    if not response.text:
        raise ValueError("Failed to summarize text.")

    return response.text


class ErrorDetail(BaseModel):
    original_error_text: str
    corrected_text: str
    error_category: Literal["spelling", "grammar"]


class ListOfErrors(BaseModel):
    errors: list[ErrorDetail]


def identify_errors_in_text(text: str):
    assert GEMINI_MODEL_ID is not None

    client = genai.Client(api_key=GEMINI_API_KEY)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL_ID,
            # model="nope",
            contents=[
                "You are an expert proof-reader. Find spelling errors in the following document",
                text,
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": ListOfErrors,
            },
        )
    except api_exceptions.APIError as e:
        logger.error(
            f"Gemini API call failed during text summarization: {e}", exc_info=True
        )
        # Option 1: Re-raise as a custom error for specific handling upstream
        raise SummarizationError(f"API call failed: {e}") from e

    # Use the response as a JSON string.
    print(response.text)

    response_parsed: ListOfErrors = response.parsed

    print(response_parsed)


#  make the script executable for testing
if __name__ == "__main__":

    editorial = """
    The Urgent Need for Media Literasy in the Digital Age
    The prolifiration of information, and misinfromation, online has reach a critical junkture. No longer can we pasively consume content; active dissernment is paramont. The ease with wich falsehoods can be dressed as truth and rapidly diseminated pose a signifcant threat to informed public discurse and even democratic proceses.
    Investing in robust media literacy educasion from an early age are not merely benefiscial, but esential. We must equip citizen's with the critcal thinking skill's to evaluate sources, identify bias, and understanding the motivasions behind the content they encunter. This isnt about cencorship, but empowermen. An informed populus, capible of distinguish credible informasion from propaganda or clickbait, is the stronggest defense against manipulasion. The responsability also lie with platfroms to promote transparancy and curb the algorithmic amplificasion of harmfull content. But ultimatly, fostering a culture of critical inquiry are our collective societal duty. The future of informed decision-making depend on it.
    """

    summary = identify_errors_in_text(editorial)

    print(summary)
