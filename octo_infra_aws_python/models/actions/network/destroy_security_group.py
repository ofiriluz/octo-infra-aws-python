from pydantic import BaseModel, Field


class DestroySecurityGroup(BaseModel):
    security_group_id: str = Field(description="ID of the security group")
