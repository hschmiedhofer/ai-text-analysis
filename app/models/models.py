from typing import Literal
from pydantic import BaseModel


class Editorial(BaseModel):
    name: str
    text: str
