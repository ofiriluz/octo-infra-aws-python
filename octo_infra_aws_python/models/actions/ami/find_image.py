from pydantic import BaseModel, Field


class FindImage(BaseModel):
    provider: str = Field()
    description: str = Field(default="*")
    name: str = Field(default="*")
