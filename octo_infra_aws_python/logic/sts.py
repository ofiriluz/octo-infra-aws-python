from typing import Optional

import boto3
from mypy_boto3_sts.client import STSClient
from mypy_boto3_sts.type_defs import GetCallerIdentityResponseTypeDef


class STS:
    @staticmethod
    def get_caller_identity_response() -> GetCallerIdentityResponseTypeDef:
        """
        Gets the caller of the current assumed STS

        :return:
        """
        sts_client: STSClient = boto3.client('sts')
        return sts_client.get_caller_identity()

    @staticmethod
    def get_account_id() -> Optional[str]:
        """
        Gets the current account id

        :return:
        """
        return STS.get_caller_identity_response().get('Account')

    @staticmethod
    def get_account_arn() -> Optional[str]:
        """
        Gets the current account arn

        :return:
        """
        return STS.get_caller_identity_response().get('Arn')
