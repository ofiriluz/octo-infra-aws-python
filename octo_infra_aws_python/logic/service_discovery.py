from octo_infra_aws_python.models.service_instance import ServiceInstance
from octo_infra_aws_python.models.actions.service_discovery import FindServiceInstance
from typing import Optional
from mypy_boto3_servicediscovery.client import ServiceDiscoveryClient
from mypy_boto3_servicediscovery.type_defs import DiscoverInstancesResponseTypeDef
import boto3
from logging import Logger, getLogger


class ServiceDiscovery:
    @staticmethod
    def find_service_instance(find_service_instance: FindServiceInstance, logger: Optional[Logger] = None) -> Optional[ServiceInstance]:
        """
        Tries to find an instance for a given filter

        :param find_service_instance:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_service_instance")
        try:
            service_discovery_client: ServiceDiscoveryClient = boto3.client("servicediscovery",
                                                                            region_name=find_service_instance.region)
            instances: DiscoverInstancesResponseTypeDef = service_discovery_client.discover_instances(
                NamespaceName=find_service_instance.namespace,
                ServiceName=find_service_instance.service,
                QueryParameters=find_service_instance.attributes_filter
            )
            if len(instances["Instances"]) > 0:
                return ServiceInstance(
                    namespace=find_service_instance.namespace,
                    service=find_service_instance.service,
                    instance=instances["Instances"][0]["InstanceId"],
                    attributes=instances["Instances"][0]["Attributes"]
                )
        except Exception as e:
            logger.exception(f"Failed discovering instance [{str(e)}]")
        return None
