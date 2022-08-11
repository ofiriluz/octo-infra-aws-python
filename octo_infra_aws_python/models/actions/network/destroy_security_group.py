from octo_infra_aws_python.models.network_rule import NetworkRule
from pydantic import BaseModel, Field
from typing import Optional, List


class DestroySecurityGroup(BaseModel):
    security_group_id: str = Field(description="ID of the security group")
