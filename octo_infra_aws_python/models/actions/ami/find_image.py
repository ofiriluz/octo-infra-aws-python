from pydantic import BaseModel, Field
from typing import Optional


class FindImage(BaseModel):
    provider: str = Field()
    description: Optional[str] = Field(default="*")
    name: Optional[str] = Field(default="*")
