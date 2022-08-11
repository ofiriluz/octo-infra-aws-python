Octo Infra AWS
=================================

[![Infra AWS Build Pipeline](https://github.com/ofiriluz/octo-infra-aws-python/actions/workflows/build.yml/badge.svg)](https://github.com/ofiriluz/octo-infra-aws-python/actions/workflows/build.yml)

Infra library for AWS operations

Encapsulates some actions in classes to easier perform actions such as VPC access or EC2 access

Installing
----------

The infra-aws requires Python 3.8+

In order to install octo-infra-aws, you can install it directly from pypi:

```bash
pip3 install octo-infra-aws-python
```

Usage
-----

The library has a few helper classes:
- EC2
- Network
- SSM
- ServiceDiscovery
- S3
- AMI
- STS

All of the helpers above supply functions to easily manage different actions

Creating / Destroying a VPC along with all its resources:
```python
gw_id: Optional[str] = Network.create_internet_gateway(CreateInternetGateway(
    internet_gateway_name="InternetGW",
    tags={"a": "b"}
))
vpc_id: Optional[str] = Network.create_vpc(CreateVPC(
    cidr_block="10.0.0.0/16",
    vpc_name="VPC",
    internet_gw=gw_id,
    is_public=True,
    tags={"a": "b"}
))
Network.destroy_vpc(DestroyVPC(
  vpc_id=vpc_id,
  full_cleanup=True
))
```

Creating EC2 Instance:
```python
EC2.create_ec2_instance(CreateEC2(
    vpc_id="vpc-12345,
    subnet_id="subnet-12345",
    instance_name="ec2",
    instance_type="t2.small",
    wait_until_finished=True,
    extra_startup_wait_time_seconds=30,
    security_group="sg-12345",
    keypair="keypair",
    ami="ami-12345",
    tags={"a": "b"},
    user_data="rm -rf"
), instance_count=3)
```

More usages can be found in code
