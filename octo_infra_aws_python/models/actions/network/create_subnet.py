from pydantic import BaseModel, Field
from typing import Optional, Dict


class CreateSubnet(BaseModel):
    cidr_block: str = Field(description="CIDR Block to use for the subnet")
    subnet_name: str = Field(description="Name of the subnet")
    availability_zone: Optional[str] = Field(description='Which AZ to put the subnet in')
    vpc_id: str = Field(description="VPC ID to create the subnet on")
    tags: Dict[str, str] = Field(description="Tags to be used for the VPC",
                                 default={})
