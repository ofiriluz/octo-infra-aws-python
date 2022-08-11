from pydantic import BaseModel, Field
from typing import Dict


class CreateInternetGateway(BaseModel):
    internet_gateway_name: str = Field()
    tags: Dict[str, str] = Field(description="Tags to be used for the Internet GW",
                                 default={})
