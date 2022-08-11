from pydantic import BaseModel, Field


class FindSSMParameter(BaseModel):
    name: str = Field()
    decrpyt: bool = Field(default=True)
