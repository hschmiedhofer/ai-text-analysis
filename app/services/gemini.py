import pathlib
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types, Client
from google.genai.chats import Chat
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch, File
from google.genai import errors as api_exceptions

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
    logger.error("Could not open log file  due to permissions.")


load_dotenv()  # Load environment variables from .env file

# Get the API key from environment variable
# TODO would this be something for the __init__.py file?
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("No GOOGLE_API_KEY found in environment variables.")

# Get the model ID from environment variable
model_id = os.getenv("MODEL_ID")
if not model_id:
    raise ValueError("No MODEL_ID found in environment variables.")

# create gemini client
client = genai.Client(api_key=api_key)


# Define a custom exception (optional, but good practice)
class SummarizationError(Exception):
    pass


def summarize_text(text_to_summarize: str, addt_prompt="Summarize this text"):
    assert model_id is not None

    try:
        response = client.models.generate_content(
            model=model_id, contents=[addt_prompt, text_to_summarize]
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


#  make the script executable for testing
if __name__ == "__main__":

    editorial = """
    The Urgent Need for Media Literacy in the Digital Age
    The proliferation of information, and misinformation, online has reached a critical juncture. No longer can we passively consume content; active discernment is paramount. The ease with which falsehoods can be dressed as truth and rapidly disseminated poses a significant threat to informed public discourse and even democratic processes.
    Investing in robust media literacy education from an early age is not merely beneficial, but essential. We must equip citizens with the critical thinking skills to evaluate sources, identify biases, and understand the motivations behind the content they encounter. This isn't about censorship, but empowerment. An informed populace, capable of distinguishing credible information from propaganda or clickbait, is the strongest defense against manipulation. The responsibility also lies with platforms to promote transparency and curb the algorithmic amplification of harmful content. But ultimately, fostering a culture of critical inquiry is our collective societal duty. The future of informed decision-making depends on it.
    """

    summary = summarize_text(editorial)

    print(summary)
