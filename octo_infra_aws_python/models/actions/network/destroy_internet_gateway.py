from pydantic import BaseModel, Field


class DestroyInternetGateway(BaseModel):
    internet_gateway_id: str = Field()
