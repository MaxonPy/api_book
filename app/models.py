from pydantic import BaseModel, Field
from typing import Optional


class Book(BaseModel):
    id: Optional[int] = None
    title: str = Field(..., max_length=255)
    author: str = Field(..., max_length=255)
    year: int
    isbn: Optional[str] = Field(None, max_length=13)