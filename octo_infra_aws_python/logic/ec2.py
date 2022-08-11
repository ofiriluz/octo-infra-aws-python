import base64
import os
import time
from datetime import datetime
from http import HTTPStatus
from typing import Final, List, Optional, Tuple, Union

import boto3
from mypy_boto3_ec2.client import EC2Client
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from mypy_boto3_ec2.service_resource import EC2ServiceResource, Image, Instance
from mypy_boto3_ec2.type_defs import (DescribeInstancesResultTypeDef,
                                      DescribeKeyPairsResultTypeDef,
                                      FilterTypeDef,
                                      GetPasswordDataResultTypeDef)

from octo_infra_aws_python.logic.ami import AMI
from octo_infra_aws_python.models.actions.ami import FindImage
from octo_infra_aws_python.models.actions.ec2 import (CreateEC2, CreateKeypair, DestroyEC2,
                                          DestroyKeypair,
                                          FindEC2InstanceCredentials)
from octo_infra_aws_python.models.find_asset import FindAsset
from octo_infra_aws_python.logic.network import Network
from logging import Logger, getLogger

FIND_EC2_CREDENTIALS_INTERVAL: Final[int] = 1
EXTRA_INSTANCE_CREATION_TIME: Final[int] = 2
DEFAULT_ADMIN_USERNAME: Final[str] = "Administrator"


class EC2:
    @staticmethod
    def create_key_pair(create_key_pair: CreateKeypair, logger: Optional[Logger] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Creates a new keypair based on the create key pair model
        Returns both the key id and key name

        :param create_key_pair:
        :param logger:
        :return:
        """
        logger = logger or getLogger("create_key_pair")
        try:
            logger.info(f"Starting creation of keypair [{create_key_pair.keypair_name}]")
            ec2_resource: EC2ServiceResource = boto3.resource("ec2")
            ec2_client: EC2Client = ec2_resource.meta.client
            # Check if the keypair already exists
            try:
                response: DescribeKeyPairsResultTypeDef = ec2_client.describe_key_pairs(
                    KeyNames=[
                        create_key_pair.keypair_name
                    ]
                )
                code: int = response['ResponseMetadata']['HTTPStatusCode']
                if code == HTTPStatus.OK:
                    if 'KeyPairs' in response and len(response['KeyPairs']) > 0:
                        # Key exists
                        if create_key_pair.delete_if_exists:
                            EC2.destroy_keypair(DestroyKeypair(keypair_name=response['KeyPairs'][0]['KeyName']), logger)
                        elif create_key_pair.use_if_exists:
                            return response['KeyPairs'][0]['KeyPairId'], response['KeyPairs'][0]['KeyName']
                        else:
                            raise Exception("Key pair already exists")
            except Exception as e:
                logger.info(f"Existing Keypair does not exist [{create_key_pair.keypair_name}]")
                logger.debug(str(e))
            create_key_pair.tags["Name"] = create_key_pair.keypair_name
            keypair = ec2_resource.create_key_pair(KeyName=create_key_pair.keypair_name,
                                                   TagSpecifications=[{"ResourceType": "key-pair",
                                                                       "Tags": [{"Key": k, "Value": v} for k, v in
                                                                                create_key_pair.tags.items()]}])
            if create_key_pair.private_key_file_path:
                if os.path.exists(create_key_pair.private_key_file_path):
                    os.remove(create_key_pair.private_key_file_path)
                with open(create_key_pair.private_key_file_path, 'w') as f:
                    f.write(keypair.key_material)
                os.chmod(create_key_pair.private_key_file_path, 0o400)
            logger.info(f"Finished creating keypair [{keypair.key_pair_id}]")
            return keypair.key_pair_id, create_key_pair.keypair_name
        except Exception as e:
            logger.exception(f"Failed creating Keypair [{str(e)}]")
        return None, None

    @staticmethod
    def destroy_keypair(destroy_keypair: DestroyKeypair, logger: Optional[Logger] = None) -> None:
        """
        Destroys the given keypair

        :param destroy_keypair:
        :param logger:
        :return:
        """
        logger = logger or getLogger("destroy_keypair")
        try:
            logger.info(f"Starting termination of keypair [{destroy_keypair.keypair_name}]")
            ec2_resource: EC2ServiceResource = boto3.resource("ec2")
            ec2_resource.KeyPair(destroy_keypair.keypair_name).delete()
            logger.info(f"Keypair deleted [{destroy_keypair.keypair_name}]")
        except Exception as e:
            logger.exception(f"Failed destroying keypair [{str(e)}]")

    @staticmethod
    def create_ec2_instance(create_ec2: CreateEC2,
                            instance_count: int = 1,
                            logger: Optional[Logger] = None) -> Optional[List[str]]:
        """
        Creates EC2 instances based on the create ec2 model

        :param create_ec2:
        :param instance_count:
        :param logger:
        :return:
        """
        logger = logger or getLogger("create_ec2_instance")
        try:
            ec2_resource: EC2ServiceResource = boto3.resource("ec2")

            # Set the security group
            security_group_id: Optional[str] = create_ec2.security_group
            if create_ec2.security_group and not isinstance(create_ec2.security_group, str):
                security_group_id = Network.create_security_group(create_ec2.security_group, logger)

            # Set the keypair
            keypair_id: Union[CreateKeypair, str] = create_ec2.keypair
            if create_ec2.keypair and not isinstance(create_ec2.keypair, str):
                _, keypair_id = EC2.create_key_pair(create_ec2.keypair, logger)

            # Set the AMI
            ami_id: Optional[str] = create_ec2.ami
            if create_ec2.ami and not isinstance(create_ec2.ami, str):
                ami_id = AMI.find_image(create_ec2.ami)
            elif not create_ec2.ami:
                ami_id = AMI.find_image(FindImage(provider="amazon",
                                                  description="Microsoft Windows Server 2019 with Desktop Experience "
                                                              "Locale English AMI provided by Amazon"))
            if not ami_id and isinstance(create_ec2.ami, str):
                ami_id = create_ec2.ami
            elif not ami_id:
                raise Exception("Failed to deduce AMI to use")

            ec2_resource: EC2ServiceResource = boto3.resource("ec2")
            logger.info(f"Starting to create EC2 Instances "
                        f"[Keypair ID: {keypair_id}, "
                        f"Security Group ID: {security_group_id}, "
                        f"AMI ID: {ami_id}, "
                        f"Count: {instance_count}]")
            create_ec2.tags["Name"] = create_ec2.instance_name
            ami: Image = ec2_resource.Image(ami_id)
            ami.load()
            block_device = [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'VolumeSize': 30,
                        'VolumeType': 'gp2',
                        'Encrypted': True
                    },
                },
            ]
            if (ami.platform and "linux" in ami.platform.lower()) or \
                    (ami.platform_details and "linux" in ami.platform_details.lower()):
                block_device = [
                    {
                        'DeviceName': '/dev/xvda',
                        'Ebs': {
                            'DeleteOnTermination': True,
                            'VolumeSize': 8,
                            'VolumeType': 'gp2',
                            'Encrypted': True
                        },
                    }
                ]
            instances: List[Instance] = ec2_resource.create_instances(
                ImageId=ami_id, MinCount=1, MaxCount=instance_count,
                BlockDeviceMappings=block_device,
                NetworkInterfaces=[{
                    "DeviceIndex": 0,
                    "SubnetId": create_ec2.subnet_id,
                    "AssociatePublicIpAddress": create_ec2.associate_public_ip,
                    "Groups": [security_group_id],
                }],
                InstanceType=create_ec2.instance_type,
                KeyName=keypair_id,
                Monitoring={'Enabled': False},
                UserData=create_ec2.user_data or '',
                TagSpecifications=[{"ResourceType": "instance",
                                   "Tags": [{"Key": k, "Value": v} for k, v in create_ec2.tags.items()]}])
            time.sleep(EXTRA_INSTANCE_CREATION_TIME)
            if create_ec2.wait_until_finished:
                for instance in instances:
                    logger.info(f"Waiting for instance to be running [{instance.id}]")
                    instance.start()
                    instance.wait_until_running()
            if create_ec2.extra_startup_wait_time_seconds:
                logger.info(f"Waiting extra startup time [{create_ec2.extra_startup_wait_time_seconds}]")
                time.sleep(create_ec2.extra_startup_wait_time_seconds)
            instances_ids: List[str] = [instance.id for instance in instances]
            if create_ec2.disable_metadata_access:
                client: EC2Client = boto3.client("ec2")
                for instance_id in instances_ids:
                    client.modify_instance_metadata_options(
                        InstanceId=instance_id,
                        HttpTokens="required",
                        HttpEndpoint="disabled"
                    )
            logger.info(f"Finished creating EC2 Instances [{instances_ids}]")
            return instances_ids
        except Exception as e:
            logger.exception(f"Failed creating EC2 instances [{str(e)}]")
        return None

    @staticmethod
    def destroy_ec2_instance(destroy_ec2: DestroyEC2, logger: Optional[Logger] = None) -> None:
        """
        Destroys an EC2 instance along with his keypair if allowed

        :param destroy_ec2:
        :param logger:
        :return:
        """
        logger = logger or getLogger("destroy_ec2_instance")
        try:
            logger.info(f"Starting termination of EC2 Instance [{destroy_ec2.instance_id}]")
            ec2_resource: EC2ServiceResource = boto3.resource("ec2")
            instance: Instance = ec2_resource.Instance(destroy_ec2.instance_id)
            if destroy_ec2.destroy_keypair:
                EC2.destroy_keypair(DestroyKeypair(keypair_name=instance.key_name), logger)
            instance.stop()
            if destroy_ec2.wait_for_stopped:
                logger.info(f"Waiting for EC2 Instance to be Stopped [{destroy_ec2.instance_id}]")
                instance.wait_until_stopped()
            instance.terminate()
            if destroy_ec2.wait_for_termination:
                logger.info(f"Waiting for EC2 Instance to be Terminated [{destroy_ec2.instance_id}]")
                instance.wait_until_terminated()
            logger.info(f"EC2 Instance Terminated [{destroy_ec2.instance_id}]")
        except Exception as e:
            logger.exception(f"Failed destroying EC2 instance [{str(e)}]")

    @staticmethod
    def find_ec2_instance_credentials(find_ec2_instance_password: FindEC2InstanceCredentials, 
                                      logger: Optional[Logger] = None) -> Tuple[Optional[str],
                                                                                Optional[str]]:
        """
        Returns username and password for the given instance info

        :param find_ec2_instance_password:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_ec2_instance_credentials")
        try:
            ec2_client: EC2Client = boto3.client("ec2")
            start = datetime.now()
            logger.info(f"Trying to get instance [{find_ec2_instance_password.instance_id}] "
                        f"password for [{find_ec2_instance_password.retry_timeout_seconds}] seconds")
            while True:
                now = datetime.now()
                if (now - start).seconds > find_ec2_instance_password.retry_timeout_seconds:
                    logger.error(f"Failed retrieving EC2 instance credentials, timeout reached [{(now - start).seconds}] seconds")
                    break
                response: GetPasswordDataResultTypeDef = ec2_client.get_password_data(
                    InstanceId=find_ec2_instance_password.instance_id)
                if response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK and \
                        response['PasswordData']:
                    with open(find_ec2_instance_password.private_key_path, 'r') as key_file:
                        key = RSA.importKey(key_file.read())
                        cipher = PKCS1_v1_5.new(key)
                        password = cipher.decrypt(base64.b64decode(response['PasswordData']), None).decode('utf8')
                        logger.info(f"Managed to retrieve password for [{find_ec2_instance_password.instance_id}] "
                                    f"after [{(datetime.now() - start).seconds}] seconds")
                        return DEFAULT_ADMIN_USERNAME, password
                time.sleep(FIND_EC2_CREDENTIALS_INTERVAL)
        except Exception as e:
            logger.exception(f"Failed retrieving EC2 instance credentials [{str(e)}]")
        return None, None

    @staticmethod
    def get_ec2_instance_properties(find_asset: FindAsset, instance_property: str, logger: Optional[Logger] = None):
        """
        Returns a given ec2 property by name

        :param find_asset:
        :param instance_property
        :param logger:
        :return:
        """
        logger = logger or getLogger("get_ec2_instance_properties")
        try:
            ec2_client: EC2Client = boto3.client('ec2')
            filters: List[FilterTypeDef] = []
            if find_asset.tags:
                filters.extend([{
                    "Name": f"tag:{key}",
                    "Values": [value]
                } for key, value in find_asset.tags.items()])
            if find_asset.state:
                filters.append({
                    "Name": f"instance-state-name",
                    "Values": [find_asset.state]
                })
            if find_asset.vpc_id:
                filters.append({
                    "Name": "vpc-id",
                    "Values": [find_asset.vpc_id]
                })
            instances_result: DescribeInstancesResultTypeDef = ec2_client.describe_instances(Filters=filters)
            if len(instances_result["Reservations"]) > 0:
                instances_ids = []
                for instances_def in instances_result["Reservations"]:
                    if len(instances_def["Instances"]) > 0:
                        instances_ids.extend([instance[instance_property] for instance in instances_def["Instances"]])
                if len(instances_ids) > 0:
                    return instances_ids
        except Exception as e:
            logger.exception(f"Failed finding instances [{str(e)}]")
        return None

    @staticmethod
    def find_ec2_instances(find_asset: FindAsset, logger: Optional[Logger] = None) -> Optional[List[str]]:
        """
        Tries to find ec2 instances based on the given asset filter

        :param find_asset:
        :param logger:
        :return:
        """
        return EC2.get_ec2_instance_properties(find_asset, "InstanceId", logger)

    @staticmethod
    def find_ec2_instance_types(find_asset: FindAsset, logger: Optional[Logger] = None) -> Optional[List[str]]:
        """
        Tries to find ec2 instance types based on the given asset filter

        :param find_asset:
        :param logger:
        :return:
        """
        return EC2.get_ec2_instance_properties(find_asset, "InstanceType", logger)
