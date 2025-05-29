import os
from dotenv import load_dotenv

import logfire
from pydantic import BaseModel
from pydantic_ai import Agent
from sqlmodel import SQLModel
from enum import Enum
import asyncio


load_dotenv()  # Load environment variables from .env file

# Get the API key from environment variable
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No GOOGLE_API_KEY found in environment variables.")

# Get the model ID from environment variable
GEMINI_MODEL_ID = os.getenv("MODEL_ID")
if not GEMINI_MODEL_ID:
    raise ValueError("No MODEL_ID found in environment variables.")


# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire="if-token-present")
logfire.instrument_pydantic_ai()


class ErrorCategoryEnum(str, Enum):
    SPELLING = "spelling"
    GRAMMAR = "grammar"
    STYLE = "style"


class ErrorDetail(BaseModel):
    original_error_text: str
    corrected_text: str
    error_category: ErrorCategoryEnum
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


class MyModel(BaseModel):
    city: str
    country: str


model = GEMINI_MODEL_ID
print(f"Using model: {model}")
agent = Agent(model, output_type=ApiResponse)


prompt = """
        You are an expert proof-reader. Find errors in the following document. 
        For each error, include error_context that starts with the original_error_text 
        and adds the following 50 characters from the original text. 
        Do not add characters that came before the original_error_text!!
        Additionally, return your summary of the text quality.
        """

document = """
        Investing in robust media literacy educasion from an early age are not merely benefiscial, but, in point of fact, esential. It is required that we must equip citizen's with the critcal thinking skill's to evaluate sources, identify bias, and understanding the motivasions that are behind the content they encunter. This isnt about cencorship, not at all, but empowermen for the people. An informed populus, capible of distinguish credible informasion from propaganda or clickbait (which is everywhere!), is the stronggest defense, a veritable shield, against manipulasion. The responsability also lie with platfroms to promote transparancy and to be curbing the algorithmic amplificasion of harmfull content. But ultimatly, fostering a culture of critical inquiry are our collective societal duty that we all share. The future of informed decision-making, it will have depended on it.
        """


async def main():
    result = await agent.run([prompt, document])
    print(result.output)
    print(result.usage())


if __name__ == "__main__":

    asyncio.run(main())
