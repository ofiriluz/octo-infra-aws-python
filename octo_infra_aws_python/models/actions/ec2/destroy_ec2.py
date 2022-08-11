from octo_infra_aws_python.models.actions.ec2.destroy_key_pair import DestroyKeypair
from pydantic import BaseModel, Field
from typing import Optional


class DestroyEC2(BaseModel):
    instance_id: str = Field(description="EC2 Instance ID to destroy")
    destroy_keypair: bool = Field(description="If given, will also delete key pair",
                                  default=True)
    wait_for_termination: bool = Field(description="Whether to fully wait for termination or not",
                                       default=True)
    wait_for_stopped: bool = Field(description="Whether to fully wait for stopped or not",
                                   default=False)
