from pydantic import BaseModel, Field
from typing import Optional


class DestroyKeypair(BaseModel):
    keypair_name: str = Field(description="Key pair name")
