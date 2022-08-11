from typing import Dict, Optional, Union

from pydantic import BaseModel, Field

from octo_infra_aws_python.models.actions.ami.find_image import FindImage
from octo_infra_aws_python.models.actions.network.create_security_group import \
    CreateSecurityGroup


class CreateEC2(BaseModel):
    vpc_id: str = Field(description="VPC of the ec2 instance to use")
    subnet_id: str = Field(description="Subnet of the ec2 instance to use")
    instance_name: str = Field(description="Name of the instance")
    instance_type: Optional[str] = Field(description="Instance type to deploy with", default="t2.micro")
    wait_until_finished: Optional[bool] = Field(description="Wait for the EC2 to finish creation",
                                                default=True)
    extra_startup_wait_time_seconds: Optional[int] = Field(description="Extra time to wait on instance to be ready")
    security_group: Union[CreateSecurityGroup, str] = Field(description="Security group to use for the instance, "
                                                                        "or a new one to create")

    keypair: Union["CreateKeypair", str] = Field(
        description="Keypair name to use for the ec2 instance, "
                    "or a new one to create")
    ami: Optional[Union[FindImage, str]] = Field(
        description="AMI to use, if not given, "
                    "windows default will be used")
    tags: Dict[str, str] = Field(description="Tags to be used for the instance",
                                 default={})
    user_data: Optional[str] = Field(description="User data to use for the instance")
    disable_metadata_access: Optional[bool] = Field(description="If set to true, will disable the metadata access")
    associate_public_ip: bool = Field(description="Whether to associate a public ip", default=True)


# Workaround for circular import of backend settings
from octo_infra_aws_python.models.actions.ec2.create_key_pair import CreateKeypair
CreateEC2.update_forward_refs()
