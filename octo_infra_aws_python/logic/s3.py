from octo_infra_aws_python.models.actions.s3 import \
    DownloadObject, DeleteObjects, UploadObject, \
    ObjectInfo, ObjectExists, FindObjects, LoadObject, SaveObject
from typing import List, Optional, Iterator
from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import \
    HeadObjectOutputTypeDef, GetObjectOutputTypeDef, PutObjectOutputTypeDef, \
    DeleteObjectsOutputTypeDef, ListObjectsOutputTypeDef
from http import HTTPStatus
from botocore.exceptions import ClientError
import boto3
import os
import fnmatch
from logging import Logger, getLogger


class S3:
    @staticmethod
    def download_object(download_object: DownloadObject, logger: Optional[Logger] = None) -> bool:
        """
        Tries to download an object from a given bucket to the filesystem

        :param download_object:
        :param logger:
        :return:
        """
        logger = logger or getLogger("download_object")
        try:
            os.makedirs(os.path.dirname(download_object.output_path), exist_ok=True)
            client: S3Client = boto3.client("s3")
            client.download_file(
                Bucket=download_object.bucket_name,
                Key=download_object.object_path,
                Filename=download_object.output_path
            )
            return True
        except Exception as e:
            logger.exception(f"Failed downloading object [{str(e)}]")
        return False

    @staticmethod
    def load_object(load_object: LoadObject, logger: Optional[Logger] = None) -> Optional[bytes]:
        """
        Tries to load an object from a given bucket and returns its raw data

        :param load_object:
        :param logger:
        :return:
        """
        logger = logger or getLogger("load_object")
        try:
            client: S3Client = boto3.client("s3")
            response: GetObjectOutputTypeDef = client.get_object(
                Bucket=load_object.bucket_name,
                Key=load_object.object_path
            )
            if response and response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK:
                return response["Body"].read()
        except Exception as e:
            logger.exception(f"Failed loading object [{str(e)}]")
        return None

    @staticmethod
    def upload_object(upload_object: UploadObject, logger: Optional[Logger] = None) -> bool:
        """
        Tries to upload a file from filesystem to a given bucket

        :param upload_object:
        :param logger:
        :return:
        """
        logger = logger or getLogger("upload_object")
        try:
            if not os.path.exists(upload_object.input_path):
                return False
            client: S3Client = boto3.client("s3")
            client.upload_file(
                Filename=upload_object.input_path,
                Bucket=upload_object.bucket_name,
                Key=upload_object.object_path
            )
            return True
        except Exception as e:
            logger.exception(f"Failed uploading object [{str(e)}]")
        return False

    @staticmethod
    def save_object(save_object: SaveObject, logger: Optional[Logger] = None) -> bool:
        """
        Tries to save raw data to a given bucket

        :param save_object:
        :param logger:
        :return:
        """
        logger = logger or getLogger("save_object")
        try:
            client: S3Client = boto3.client("s3")
            response: PutObjectOutputTypeDef = client.put_object(
                Bucket=save_object.bucket_name,
                Key=save_object.object_path,
                Body=save_object.body
            )
            return response and response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        except Exception as e:
            logger.exception(f"Failed saving object [{str(e)}]")
        return False

    @staticmethod
    def delete_objects(delete_objects: DeleteObjects, logger: Optional[Logger] = None) -> bool:
        """
        Tries to delete an object from the bucket

        :param delete_objects:
        :param logger:
        :return:
        """
        logger = logger or getLogger("delete_objects")
        try:
            client: S3Client = boto3.client("s3")
            response: DeleteObjectsOutputTypeDef = client.delete_objects(
                Bucket=delete_objects.bucket_name,
                Delete={
                    "Objects": [
                        {"Key": key} for key in delete_objects.objects_path
                    ]
                }
            )
            return response and response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        except Exception as e:
            logger.exception(f"Failed deleting object [{str(e)}]")
        return False

    @staticmethod
    def find_objects(find_objects: FindObjects, logger: Optional[Logger] = None) -> Optional[List[ObjectInfo]]:
        """
        Tries to find all objects fitting the given filters on the bucket

        :param find_objects:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_objects")
        try:
            client: S3Client = boto3.client("s3")
            paginator = client.get_paginator('list_objects')
            params = {
                "Bucket": find_objects.bucket_name,
                "Prefix": find_objects.base_search_path
            }
            if find_objects.only_prefixes:
                params["Delimiter"] = "/"
            page_iterator: Iterator[ListObjectsOutputTypeDef] = paginator.paginate(
                **params
            )
            objects: List[ObjectInfo] = []
            for page in page_iterator:
                if page["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK:
                    if find_objects.only_prefixes:
                        for prefix in page.get("CommonPrefixes", []):
                            if len(find_objects.filters) == 0 or \
                                    any(fnmatch.fnmatch(prefix["Prefix"], pattern) for pattern in find_objects.filters):
                                objects.append(ObjectInfo(
                                    bucket_name=find_objects.bucket_name,
                                    object_path=prefix["Prefix"],
                                    object_size=0,
                                    is_folder=prefix["Prefix"].endswith("/")
                                ))
                    else:
                        for obj in page.get("Contents", []):
                            if len(find_objects.filters) == 0 or \
                                    any(fnmatch.fnmatch(obj["Key"], pattern) for pattern in find_objects.filters):
                                objects.append(ObjectInfo(
                                    bucket_name=find_objects.bucket_name,
                                    object_path=obj["Key"],
                                    object_size=obj["Size"],
                                    is_folder=obj["Key"].endswith("/")
                                ))
            return objects
        except Exception as e:
            logger.exception(f"Failed finding objects [{str(e)}]")
        return None

    @staticmethod
    def object_exists(object_exists: ObjectExists, logger: Optional[Logger] = None) -> bool:
        """
        Checks if the given object exists in the bucket

        :param object_exists:
        :param logger:
        :return:
        """
        logger = logger or getLogger("object_exists")
        try:
            client: S3Client = boto3.client("s3")
            response: HeadObjectOutputTypeDef = client.head_object(
                Bucket=object_exists.bucket_name,
                Key=object_exists.object_path
            )
            return response and response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
        except ClientError:
            logger.debug(f"Object not found")
        except Exception as e:
            logger.exception(f"Failed checking if object exists [{str(e)}]")
        return False
