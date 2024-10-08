from octo_infra_aws_python.models.network_rule import NetworkRule
from pydantic import BaseModel, Field
from typing import List, Dict


class CreateSecurityGroup(BaseModel):
    name: str = Field(description="Name of the security group")
    vpc_id: str = Field(description="VPC of the security group to use")
    description: str = Field(description="Description of the group", default="")
    ingress: List[NetworkRule] = Field(description="Ingress rules for a new security group",
                                       default_factory=list)
    egress: List[NetworkRule] = Field(description="Egress rules for a new security group",
                                      default_factory=list)
    tags: Dict[str, str] = Field(description="Tags to be used for the VPC",
                                 default_factory=dict)
