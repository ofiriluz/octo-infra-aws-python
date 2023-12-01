from octo_infra_aws_python.models.actions.network import \
    CreateSecurityGroup, DestroySecurityGroup, \
    CreateVPC, DestroyVPC, \
    CreateInternetGateway, DestroyInternetGateway, \
    CreateSubnet, DestroySubnet
from octo_infra_aws_python.models.find_asset import FindAsset
from typing import Optional, Any, Union, List, Final
import boto3
from mypy_boto3_ec2.client import EC2Client
from mypy_boto3_ec2.service_resource import EC2ServiceResource, Vpc, InternetGateway, Subnet
from mypy_boto3_ec2.type_defs import DescribeVpcsResultTypeDef, \
    DescribeInternetGatewaysResultTypeDef, DescribeSecurityGroupsResultTypeDef, \
    DescribeSubnetsResultTypeDef, FilterTypeDef
from concurrent.futures import ThreadPoolExecutor, wait
import time
from logging import Logger, getLogger

EXTRA_CREATION_SLEEP_TIME_SECONDS: Final[int] = 2


class Network:
    @staticmethod
    def create_security_group(create_security_group: CreateSecurityGroup, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Tries to create a security group for the given name and info
        Will also add ingress and egress to the SG if possible

        :param create_security_group:
        :param logger:
        :return:
        """
        logger = logger or getLogger("create_security_group")
        try:
            logger.info(f"Starting to create security group [{create_security_group.name}]")
            ec2_resource: EC2ServiceResource = boto3.resource("ec2")
            create_security_group.tags["Name"] = create_security_group.name
            security_group = ec2_resource.create_security_group(GroupName=create_security_group.name,
                                                                Description=create_security_group.description,
                                                                VpcId=create_security_group.vpc_id)
            time.sleep(EXTRA_CREATION_SLEEP_TIME_SECONDS)
            security_group.create_tags(Tags=[{"Key": k, "Value": v} for k, v in create_security_group.tags.items()])
            if create_security_group.ingress:
                for rule in create_security_group.ingress:
                    security_group.authorize_ingress(IpPermissions=[{'IpProtocol': rule.protocol,
                                                                     'FromPort': rule.from_port,
                                                                     'ToPort': rule.to_port,
                                                                     'IpRanges':
                                                                         [{"CidrIp": v, "Description": "Automated Rule"}
                                                                          for v in rule.allowed_cidr],
                                                                     'UserIdGroupPairs':
                                                                         [{'UserIdGroupPairs': v, "Description": "Automated Rule"}
                                                                          for v in rule.allowed_groups]}])
            if create_security_group.egress:
                for rule in create_security_group.egress:
                    security_group.authorize_egress(IpPermissions=[{'IpProtocol': rule.protocol,
                                                                    'FromPort': rule.from_port,
                                                                    'ToPort': rule.to_port,
                                                                    'IpRanges':
                                                                        [{"CidrIp": v, "Description": "Automated Rule"}
                                                                         for v in rule.allowed_cidr],
                                                                    'UserIdGroupPairs':
                                                                        [{'UserIdGroupPairs': v,
                                                                          "Description": "Automated Rule"}
                                                                         for v in rule.allowed_groups]}])
            logger.info(f"Security group created with ID [{security_group.id}]")
            return security_group.id
        except Exception as e:
            logger.exception(f"Failed creating security group [{str(e)}]")
        return None

    @staticmethod
    def destroy_security_group(destroy_security_group: DestroySecurityGroup, logger: Optional[Logger] = None) -> None:
        """
        Destroys a security group based on the given group id

        :param destroy_security_group:
        :param logger:
        :return:
        """
        logger = logger or getLogger("destroy_security_group")
        try:
            logger.info(f"Starting to destroy security group [{destroy_security_group.security_group_id}]")
            ec2_client: EC2Client = boto3.client("ec2")
            ec2_client.delete_security_group(GroupId=destroy_security_group.security_group_id)
            logger.info(f"Security group destroyed [{destroy_security_group.security_group_id}]")
        except Exception as e:
            logger.exception(f"Failed destroying security group [{str(e)}]")

    @staticmethod
    def find_security_groups(find_asset: FindAsset, logger: Optional[Logger] = None) -> Optional[List[str]]:
        """
        Tries to find security groups based on the assets filters

        :param find_asset:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_security_groups")
        try:
            ec2_client: EC2Client = boto3.client('ec2')
            filters: List[FilterTypeDef] = []
            if find_asset.tags:
                logger.info(f"Trying to find security group with tags [{find_asset.tags}]")
                filters.extend([{
                    "Name": f"tag:{key}",
                    "Values": [value]
                } for key, value in find_asset.tags.items()])
            if find_asset.vpc_id:
                logger.info(f"Trying to find security group with VPC ID [{find_asset.vpc_id}]")
                filters.append({
                    "Name": "vpc-id",
                    "Values": [find_asset.vpc_id]
                })
            security_groups: DescribeSecurityGroupsResultTypeDef = ec2_client.describe_security_groups(Filters=filters)
            if len(security_groups["SecurityGroups"]) > 0:
                return [sg["GroupId"] for sg in security_groups["SecurityGroups"]]
        except Exception as e:
            logger.exception(f"Failed finding security groups [{str(e)}]")
        return None

    @staticmethod
    def create_internet_gateway(create_internet_gateway: CreateInternetGateway, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Creates a new internet gateway and adds the given tags along with name tag to it

        :param create_internet_gateway:
        :param logger:
        :return:
        """
        logger = logger or getLogger("create_internet_gateway")
        try:
            logger.info(f"Starting to create internet gateway [{create_internet_gateway.internet_gateway_name}]")
            ec2_resource = boto3.resource("ec2")
            internet_gw: InternetGateway = ec2_resource.create_internet_gateway()
            time.sleep(EXTRA_CREATION_SLEEP_TIME_SECONDS)
            create_internet_gateway.tags["Name"] = create_internet_gateway.internet_gateway_name
            internet_gw.reload()
            internet_gw.create_tags(Tags=[{"Key": k, "Value": v} for k, v in create_internet_gateway.tags.items()])
            logger.info(f"Internet gateway created [{internet_gw.id}]")
            return internet_gw.id
        except Exception as e:
            logger.exception(f"Failed creating internet gateway [{str(e)}]")
        return None

    @staticmethod
    def destroy_internet_gateway(destroy_internet_gateway: DestroyInternetGateway, logger: Optional[Logger] = None) -> None:
        """
        Destroys an internet gateway by a given id

        :param destroy_internet_gateway:
        :param logger:
        :return:
        """
        logger = logger or getLogger("destroy_internet_gateway")
        try:
            logger.info(f"Starting to destroy internet gateway [{destroy_internet_gateway.internet_gateway_id}]")
            ec2_client: EC2Client = boto3.client("ec2")
            ec2_client.delete_internet_gateway(InternetGatewayId=destroy_internet_gateway.internet_gateway_id)
            logger.info(f"Destroyed internet gateway [{destroy_internet_gateway.internet_gateway_id}]")
        except Exception as e:
            logger.exception(f"Failed destroying internet gateway [{str(e)}]")

    @staticmethod
    def find_internet_gateway(find_asset: FindAsset, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Tries to find a fitting internet gateway based on the assets filter

        :param find_asset:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_internet_gateway")
        try:
            ec2_client: EC2Client = boto3.client('ec2')
            filters: List[FilterTypeDef] = []
            if find_asset.tags:
                logger.info(f"Trying to find internet GW with tags [{find_asset.tags}]")
                filters.extend([{
                    "Name": f"tag:{key}",
                    "Values": [value]
                } for key, value in find_asset.tags.items()])
            if find_asset.vpc_id:
                logger.info(f"Trying to find internet GW with VPC ID [{find_asset.vpc_id}]")
                filters.append({
                    "Name": "attachment.vpc-id",
                    "Values": [find_asset.vpc_id]
                })
            internet_gws: DescribeInternetGatewaysResultTypeDef = ec2_client.describe_internet_gateways(Filters=filters)
            if len(internet_gws["InternetGateways"]) > 0:
                return internet_gws["InternetGateways"][0]['InternetGatewayId']
        except Exception as e:
            logger.exception(f"Failed finding internet gateway [{str(e)}]")
        return None

    @staticmethod
    def create_vpc(create_vpc: CreateVPC, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Creates a new VPC for the given name with CIDR block and attach to the internet GW

        :param create_vpc:
        :param logger:
        :return:
        """
        logger = logger or getLogger("create_vpc")
        try:
            internet_gw_id: Union[CreateInternetGateway, str] = create_vpc.internet_gw
            if isinstance(create_vpc.internet_gw, CreateInternetGateway):
                internet_gw_id = Network.create_internet_gateway(create_vpc.internet_gw)
            logger.info(f"Starting to create VPC [{create_vpc.vpc_name}]")
            ec2_resource: EC2ServiceResource = boto3.resource("ec2")
            vpc: Vpc = ec2_resource.create_vpc(CidrBlock=create_vpc.cidr_block)
            vpc.wait_until_available()
            time.sleep(EXTRA_CREATION_SLEEP_TIME_SECONDS)
            create_vpc.tags["Name"] = create_vpc.vpc_name
            vpc.create_tags(Tags=[{"Key": k, "Value": v} for k, v in create_vpc.tags.items()])
            vpc.attach_internet_gateway(InternetGatewayId=internet_gw_id)
            vpc.modify_attribute(EnableDnsHostnames={
                "Value": True
            })
            vpc.modify_attribute(EnableDnsSupport={
                "Value": True
            })
            if create_vpc.is_public:
                main_route_table = list(
                    vpc.route_tables.filter(Filters=[{
                        'Name': 'vpc-id',
                        'Values': [vpc.id]
                    }, {
                        'Name': 'association.main',
                        'Values': ['true']
                    }]))[0]
                main_route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=internet_gw_id)
            logger.info(f"VPC created with ID [{vpc.id}]")
            return vpc.id
        except Exception as e:
            logger.exception(f"Failed creating VPC [{str(e)}]")
        return None

    @staticmethod
    def __destroy_vpc_instances(vpc_id: str, vpc: Vpc, logger: Optional[Logger] = None) -> None:
        """
        Destroys all instances related to the VPC in parallel

        :param vpc_id:
        :param vpc:
        :param logger:
        :return:
        """
        from octo_infra_aws_python.logic.ec2 import EC2
        from octo_infra_aws_python.models.actions.ec2 import DestroyEC2
        logger = logger or getLogger("__destroy_vpc_instances")
        logger.info(f"Destroying VPC Instances [{vpc_id}]")
        # Parallel instance termination due to waiting for actual termination to happen
        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = []
            for subnet in vpc.subnets.all():
                for instance in subnet.instances.all():
                    futures.append(executor.submit(EC2.destroy_ec2_instance,
                                                   DestroyEC2(
                                                       instance_id=instance.id,
                                                       destroy_keypair=True
                                                   ), logger))
            wait(futures)

    @staticmethod
    def __destroy_vpc_internet_gateways(vpc_id: str, vpc: Vpc, logger: Optional[Logger] = None) -> None:
        """
        Destroys the VPC related internet gateways

        :param vpc_id:
        :param vpc:
        :param logger:
        :return:
        """
        logger = logger or getLogger("__destroy_vpc_internet_gateways")
        logger.info(f"Destroying VPC Internet Gateways [{vpc_id}]")
        for gw in vpc.internet_gateways.all():
            vpc.detach_internet_gateway(InternetGatewayId=gw.id)
            Network.destroy_internet_gateway(DestroyInternetGateway(
                internet_gateway_id=gw.id
            ), logger)

    @staticmethod
    def __destroy_vpc_routing_tables(vpc_id: str, vpc: Vpc, logger: Optional[Logger] = None) -> None:
        """
        Destroys the VPC routing tables

        :param vpc_id:
        :param vpc:
        :param logger:
        :return:
        """
        logger = logger or getLogger("__destroy_vpc_internet_gateways")
        logger.info(f"Destroying VPC Route Tables [{vpc_id}]")
        for rt in vpc.route_tables.all():
            for rta in rt.associations:
                if not rta.main:
                    rta.delete()
            if not rt.associations:
                rt.delete()

    @staticmethod
    def __destroy_vpc_endpoints(vpc_id: str, logger: Optional[Logger] = None) -> None:
        """
        Destroys any related VPC endpoints

        :param vpc_id:
        :param logger:
        :return:
        """
        logger = logger or getLogger("__destroy_vpc_endpoints")
        ec2_client: EC2Client = boto3.client('ec2')
        logger.info(f"Destroying VPC Endpoints [{vpc_id}]")
        for ep in ec2_client.describe_vpc_endpoints(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['VpcEndpoints']:
            ec2_client.delete_vpc_endpoints(VpcEndpointIds=[ep['VpcEndpointId']])

    @staticmethod
    def __destroy_vpc_security_groups(vpc_id: str, vpc: Vpc, logger: Optional[Logger] = None) -> None:
        """
        Destroys any VPC related security groups

        :param vpc_id:
        :param vpc:
        :param logger:
        :return:
        """
        logger = logger or getLogger("__destroy_vpc_security_groups")
        logger.info(f"Destroying VPC Security Groups [{vpc_id}]")
        for sg in vpc.security_groups.all():
            if sg.group_name != 'default':
                Network.destroy_security_group(DestroySecurityGroup(security_group_id=sg.id), logger)

    @staticmethod
    def __destroy_vpc_peers(vpc_id: str, logger: Optional[Logger] = None) -> None:
        """
        Destroys any related VPC peers

        :param vpc_id:
        :param logger:
        :return:
        """
        logger = logger or getLogger("__destroy_vpc_peers")
        ec2_resource: EC2ServiceResource = boto3.resource('ec2')
        ec2_client: EC2Client = ec2_resource.meta.client
        logger.info(f"Destroying VPC Peers [{vpc_id}]")
        for vpc_peer in ec2_client.describe_vpc_peering_connections(Filters=[{
            'Name': 'requester-vpc-info.vpc-id',
            'Values': [vpc_id]
        }])['VpcPeeringConnections']:
            ec2_resource.VpcPeeringConnection(vpc_peer['VpcPeeringConnectionId']).delete()

    @staticmethod
    def __destroy_vpc_nacls(vpc_id: str, vpc: Vpc, logger: Optional[Logger] = None) -> None:
        """
        Destroys any related VPC network ACL's

        :param vpc_id:
        :param vpc:
        :param logger:
        :return:
        """
        logger = logger or getLogger("__destroy_vpc_nacls")
        logger.info(f"Destroying VPC NACLS [{vpc_id}]")
        for netacl in vpc.network_acls.all():
            if not netacl.is_default:
                netacl.delete()

    @staticmethod
    def __destroy_vpc_subnets(vpc_id: str, vpc: Vpc, logger: Optional[Logger] = None) -> None:
        """
        Destroys VPC related subnets

        :param vpc_id:
        :param vpc:
        :param logger:
        :return:
        """
        logger = logger or getLogger("__destroy_vpc_subnets")
        logger.info(f"Destroying VPC Subnets [{vpc_id}]")
        for subnet in vpc.subnets.all():
            for interface in subnet.network_interfaces.all():
                interface.delete()
            Network.destroy_subnet(DestroySubnet(subnet_id=subnet.id), logger)

    @staticmethod
    def destroy_vpc(destroy_vpc: DestroyVPC, logger: Optional[Logger] = None) -> None:
        """
        Destroys the VPC, if full cleanup is given, will also attempt to destroy the following:
        - Routing Tables
        - EC2 Instances
        - VPC Endpoints
        - VPC Peers
        - Security Groups
        - NACLS
        - Subnets
        :param destroy_vpc:
        :param logger:
        :return:
        """
        logger = logger or getLogger("destroy_vpc")
        try:
            logger.info(f"Starting to destroy VPC [{destroy_vpc.vpc_id}]")
            ec2_resource: EC2ServiceResource = boto3.resource('ec2')
            ec2_client: EC2Client = ec2_resource.meta.client
            vpc: Vpc = ec2_resource.Vpc(destroy_vpc.vpc_id)

            dhcp_options_default = ec2_resource.DhcpOptions('default')
            if dhcp_options_default:
                dhcp_options_default.associate_with_vpc(VpcId=destroy_vpc.vpc_id)

            if destroy_vpc.full_cleanup:
                # Terminate any EC2 Instances
                Network.__destroy_vpc_instances(destroy_vpc.vpc_id, vpc, logger)

                # Delete Internet Gateways
                Network.__destroy_vpc_internet_gateways(destroy_vpc.vpc_id, vpc, logger)

                # Delete Routing tables
                Network.__destroy_vpc_routing_tables(destroy_vpc.vpc_id, vpc, logger)

                # Delete VPC Endpoints
                Network.__destroy_vpc_endpoints(destroy_vpc.vpc_id, logger)

                # Delete Security Groups
                Network.__destroy_vpc_security_groups(destroy_vpc.vpc_id, vpc, logger)

                # Delete VPC Peers
                Network.__destroy_vpc_peers(destroy_vpc.vpc_id, logger)

                # Delete NACLS
                Network.__destroy_vpc_nacls(destroy_vpc.vpc_id, vpc, logger)

                # Delete Subnets
                Network.__destroy_vpc_subnets(destroy_vpc.vpc_id, vpc, logger)
            # Delete VPC
            ec2_client.delete_vpc(VpcId=destroy_vpc.vpc_id)
            logger.info(f"Destroyed VPC [{destroy_vpc.vpc_id}]")
        except Exception as e:
            logger.exception(f"Failed destroying VPC [{str(e)}]")

    @staticmethod
    def find_vpc(find_asset: FindAsset, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Tries to find a vpc for a given asset filter

        :param find_asset:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_vpc")
        try:
            ec2_resource: EC2ServiceResource = boto3.resource('ec2')
            ec2_client: EC2Client = ec2_resource.meta.client
            if find_asset.vpc_id:
                # Just make sure the VPC exists for the given ID
                logger.info(f"Trying to find VPC with VPC ID [{find_asset.vpc_id}]")
                ec2_resource.Vpc(find_asset.vpc_id)
                return find_asset.vpc_id
            elif find_asset.tags:
                logger.info(f"Trying to find VPC with tags [{find_asset.tags}]")
                vpcs: DescribeVpcsResultTypeDef = ec2_client.describe_vpcs(Filters=[{
                    "Name": f"tag:{key}",
                    "Values": [value]
                } for key, value in find_asset.tags.items()])
                if len(vpcs["Vpcs"]) > 0:
                    return vpcs["Vpcs"][0]["VpcId"]
        except Exception as e:
            logger.exception(f"Failed finding VPC [{str(e)}]")
        return None

    @staticmethod
    def create_subnet(create_subnet: CreateSubnet, logger: Optional[Logger] = None) -> Optional[str]:
        """
        Creates a new subnet and associates it with the given VPC routing table

        :param create_subnet:
        :param logger:
        :return:
        """
        logger = logger or getLogger("create_subnet")
        try:
            logger.info(f"Starting to create subnet [{create_subnet.subnet_name}]")
            ec2_resource: EC2ServiceResource = boto3.resource("ec2")
            params = {
                "CidrBlock": create_subnet.cidr_block,
                "VpcId": create_subnet.vpc_id,
            }
            if create_subnet.availability_zone:
                params['AvailabilityZone'] = create_subnet.availability_zone
            subnet: Subnet = ec2_resource.create_subnet(**params)
            time.sleep(EXTRA_CREATION_SLEEP_TIME_SECONDS)
            create_subnet.tags["Name"] = create_subnet.subnet_name
            subnet.create_tags(Tags=[{"Key": k, "Value": v} for k, v in create_subnet.tags.items()])
            main_route_table = list(
                ec2_resource.route_tables.filter(Filters=[{
                    'Name': 'vpc-id',
                    'Values': [create_subnet.vpc_id]
                }, {
                    'Name': 'association.main',
                    'Values': ['true']
                }]))[0]
            main_route_table.associate_with_subnet(SubnetId=subnet.id)
            logger.info(f"Subnet created [{subnet.id}]")
            return subnet.id
        except Exception as e:
            logger.exception(f"Failed creating Subnet [{str(e)}]")
        return None

    @staticmethod
    def destroy_subnet(destroy_subnet: DestroySubnet, logger: Optional[Logger] = None) -> None:
        """
        Destroys a subnet for the given subnet id

        :param destroy_subnet:
        :param logger:
        :return:
        """
        logger = logger or getLogger("destroy_subnet")
        try:
            logger.info(f"Starting to destroy subnet [{destroy_subnet.subnet_id}]")
            ec2_client: EC2Client = boto3.client("ec2")
            ec2_client.delete_subnet(SubnetId=destroy_subnet.subnet_id)
            logger.info(f"Destroyed subnet [{destroy_subnet.subnet_id}]")
        except Exception as e:
            logger.exception(f"Failed destroying Subnet [{str(e)}]")

    @staticmethod
    def find_subnets(find_asset: FindAsset, logger: Optional[Logger] = None) -> Optional[List[str]]:
        """
        Tries to find subnets based on the given asset filter

        :param find_asset:
        :param logger:
        :return:
        """
        logger = logger or getLogger("find_subnets")
        try:
            ec2_client: EC2Client = boto3.client('ec2')
            filters: List[FilterTypeDef] = []
            if find_asset.tags:
                logger.info(f"Trying to find subnet with tags [{find_asset.tags}]")
                filters.extend([{
                    "Name": f"tag:{key}",
                    "Values": [value]
                } for key, value in find_asset.tags.items()])
            if find_asset.vpc_id:
                logger.info(f"Trying to find subnet with VPC ID [{find_asset.vpc_id}]")
                filters.append({
                    "Name": "vpc-id",
                    "Values": [find_asset.vpc_id]
                })
            subnets: DescribeSubnetsResultTypeDef = ec2_client.describe_subnets(Filters=filters)
            if len(subnets["Subnets"]) > 0:
                return [subnet["SubnetId"] for subnet in subnets["Subnets"]]
        except Exception as e:
            logger.exception(f"Failed finding subnets [{str(e)}]")
        return None
