from pydantic import BaseModel, Field


class DestroySubnet(BaseModel):
    subnet_id: str = Field()
