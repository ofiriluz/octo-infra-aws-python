from pydantic import BaseModel, Field


class CreateSSMParameter(BaseModel):
    name: str = Field()
    value: str = Field()
    description: str = Field(default="")
    encrypt: bool = Field(default=True)
