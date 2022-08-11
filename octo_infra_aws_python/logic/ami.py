from octo_infra_aws_python.models.actions.ami.find_image import FindImage
from typing import Optional, List
import boto3
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_ec2.type_defs import DescribeImagesResultTypeDef, ImageTypeDef
from logging import Logger, getLogger


class AMI:
    @staticmethod
    def find_image(find_image: FindImage, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Tries to find an image id for a given filter

        :param find_image:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_image")
        try:
            logger.info(f"Searching for AMI [Provider={find_image.provider}, "
                        f"Name={find_image.name}, "
                        f"Description={find_image.description}]")
            ec2_client: EC2Client = boto3.client('ec2')
            filters = [{
                'Name': 'name',
                'Values': [find_image.name]
            }, {
                'Name': 'description',
                'Values': [find_image.description]
            }, {
                'Name': 'state',
                'Values': ['available']
            }]

            images: DescribeImagesResultTypeDef = ec2_client.describe_images(Filters=filters,
                                                                             Owners=[find_image.provider])
            images_info: List[ImageTypeDef] = images['Images']
            if len(images_info) == 0:
                raise RuntimeError("No AMIs were found for the given filter")
            images_info.sort(key=lambda elem: elem['CreationDate'], reverse=True)
            image_id: str = images_info[0]["ImageId"]
            logger.info(f"AMI Image Found [Image ID = {image_id}]")
            return image_id
        except Exception as e:
            logger.exception(f"Failed to find image [{str(e)}]")
        return None
