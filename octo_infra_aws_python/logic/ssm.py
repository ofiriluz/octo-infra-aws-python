from octo_infra_aws_python.models.actions.ssm import CreateSSMParameter, DestroySSMParameter, FindSSMParameter
from typing import Optional
import boto3
from http import HTTPStatus
from mypy_boto3_ssm.client import SSMClient
from mypy_boto3_ssm.literals import ParameterTypeType
from mypy_boto3_ssm.type_defs import PutParameterResultTypeDef, GetParameterResultTypeDef, DescribeParametersResultTypeDef
from logging import Logger, getLogger


class SSM:
    @staticmethod
    def create_ssm_parameter(create_ssm_parameter: CreateSSMParameter, logger: Optional[Logger] = None) -> bool:
        """
        Creates an SSM parameter from the given info

        :param create_ssm_parameter:
        :param logger:
        :return:
        """
        logger = logger or getLogger("create_ssm_parameter")
        try:
            logger.info(f"Starting creation of SSM parameter [{create_ssm_parameter.name}]")
            ssm_client: SSMClient = boto3.client("ssm")
            key_type: ParameterTypeType = "String"
            if create_ssm_parameter.encrypt:
                key_type = "SecureString"
            response: PutParameterResultTypeDef = ssm_client.put_parameter(Name=create_ssm_parameter.name,
                                                                           Value=create_ssm_parameter.value,
                                                                           Description=create_ssm_parameter.description,
                                                                           Type=key_type)
            if response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK:
                logger.info(f"SSM Parameter created [{create_ssm_parameter.name}]")
                return True
        except Exception as e:
            logger.exception(f"Failed creating SSM Parameter [{str(e)}]")
        return False

    @staticmethod
    def destroy_ssm_parameter(destroy_ssm_parameter: DestroySSMParameter, logger: Optional[Logger] = None) -> None:
        """
        Deletes an SSM parameter from the given info

        :param destroy_ssm_parameter:
        :param logger:
        :return:
        """
        logger = logger or getLogger("destroy_ssm_parameter")
        try:
            logger.info(f"Starting to destroy SSM parameter [{destroy_ssm_parameter.name}]")
            ssm_client: SSMClient = boto3.client("ssm")
            ssm_client.delete_parameter(Name=destroy_ssm_parameter.name)
            logger.info(f"SSM Parameter destroyed [{destroy_ssm_parameter.name}]")
        except Exception as e:
            logger.exception(f"Failed destroying SSM Parameter [{str(e)}]")

    @staticmethod
    def find_ssm_parameter(find_ssm_parameter: FindSSMParameter, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Finds an SSM parameter from the given info

        :param find_ssm_parameter:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_ssm_parameter")
        try:
            logger.info(f"Starting to search for SSM parameter [{find_ssm_parameter.name}]")
            ssm_client: SSMClient = boto3.client("ssm")
            response: GetParameterResultTypeDef = ssm_client.get_parameter(Name=find_ssm_parameter.name,
                                                                           WithDecryption=find_ssm_parameter.decrpyt)
            if response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK and response["Parameter"]:
                logger.info(f"SSM Parameter found [{find_ssm_parameter.name}]")
                return response["Parameter"]["Value"]
        except Exception as e:
            logger.exception(f"Failed to find SSM Parameter [{str(e)}]")
        return None

    @staticmethod
    def has_ssm_parameter(find_ssm_parameter: FindSSMParameter, logger: Optional[Logger] = None) -> bool:
        """
        Checks if an SSM parameter exists from the given info

        :param find_ssm_parameter:
        :param logger:
        :return:
        """
        logger = logger or getLogger("has_ssm_parameter")
        try:
            logger.info(f"Starting to search for SSM parameter [{find_ssm_parameter.name}]")
            ssm_client: SSMClient = boto3.client("ssm")
            response: DescribeParametersResultTypeDef = ssm_client.describe_parameters(Filters=[
                {
                    "Key": "Name",
                    "Values": [find_ssm_parameter.name]
                }
            ])
            if response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK and len(response["Parameters"]) > 0:
                logger.info(f"SSM Parameter found [{find_ssm_parameter.name}]")
                return True
        except Exception as e:
            logger.exception(f"Failed to find SSM Parameter [{str(e)}]")
        return False
