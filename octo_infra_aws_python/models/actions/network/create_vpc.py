from octo_infra_aws_python.models.actions.network.create_internet_gateway import CreateInternetGateway
from pydantic import BaseModel, Field
from typing import Union, Dict


class CreateVPC(BaseModel):
    cidr_block: str = Field(description="CIDR Block to use for the VPC subnet")
    vpc_name: str = Field(description="VPC Name")
    internet_gw: Union[CreateInternetGateway, str] = Field(description="Internet GW ID, "
                                                                       "or create a new one")
    is_public: bool = Field(description="Whether the VPC should be public gateway wise",
                            default=True)
    tags: Dict[str, str] = Field(description="Tags to be used for the VPC",
                                 default={})
