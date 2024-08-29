from pydantic import BaseModel, Field


class DestroyKeypair(BaseModel):
    keypair_name: str = Field(description="Key pair name")
