from pydantic import BaseModel, Field


class DestroyVPC(BaseModel):
    vpc_id: str = Field()
    full_cleanup: bool = Field(description="Whether to delete internet GW, "
                                           "Routing Tables, EC2 Instances, VPC Endpoints, "
                                           "VPC Peers, Security Groups, NACLS, Subnets",
                               default=True)
