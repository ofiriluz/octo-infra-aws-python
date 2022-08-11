from pydantic import BaseModel, Field


class DestroySSMParameter(BaseModel):
    name: str = Field()
