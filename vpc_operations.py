import boto3
import time
from datetime import datetime


region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)


def create_vpc():
    vpc_name = f'vpc-{datetime.now().strftime("%Y%m%d%H%M%S")}'

    response = ec2.describe_vpcs(Filters=[{"Name": "tag:Name", "Values": [vpc_name]}])

    vpcs = response.get('Vpcs', [])

    if vpcs:
        vpc_id = vpcs[0]['VpcId']
        print(f"VPC {vpc_name} with ID {vpc_id} already exists.")
  
    vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc_response['Vpc']['VpcId']

    ec2.modify_vpc_attribute(
        VpcId=vpc_id, 
        EnableDnsSupport={'Value': True}, 
        EnableDnsHostnames={'Value': True}
    )

    ec2.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": vpc_name}])

    time.sleep(3)

    print(f"VPC {vpc_name} with ID {vpc_id} has been created sucessfully!")

    return vpc_id


def create_internet_gateway(vpc_id):
    ig_name = f'ig-{datetime.now().strftime("%Y%m%d%H%M%S")}'

    response = ec2.describe_internet_gateways(Filters=[{"Name": "tag:Name", "Values": [ig_name]}])

    igs = response.get('InternetGateways', [])

    if igs:
        ig_id = igs[0]['InternetGatewayId']
        print(f"Internet Gateway {ig_name} with ID {ig_id} already exists.")
    
    ig_response = ec2.create_internet_gateway()
    ig_id = ig_response['InternetGateway']['InternetGatewayId']

    ec2.create_tags(Resources=[ig_id], Tags=[{"Key": "Name", "Value": ig_name}])
    ec2.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=ig_id)

    time.sleep(3)

    print(f"Internet Gateway {ig_name} with ID {ig_id} has been created sucessfully!")

    return ig_id


def create_route_table(vpc_id, ig_id):
    rt_name = f'rt-{datetime.now().strftime("%Y%m%d%H%M%S")}'

    response = ec2.describe_route_tables(
        Filters=[
             {"Name": "tag:Name", "Values": [rt_name]}
        ]
    )
    route_tables = response.get('RouteTables', [])

    if route_tables:
        rt_id = route_tables[0]['RouteTableId']
        print(f"Route Table {rt_name} with ID {rt_id} already exists.")


    route_table_response = ec2.create_route_table(VpcId=vpc_id)
    rt_id = route_table_response['RouteTable']['RouteTableId']

    create_params = {
        'RouteTableId': rt_id,
        'DestinationCidrBlock': '0.0.0.0/0',
        'GatewayId': ig_id
    }

    time.sleep(2)

    ec2.create_tags(Resources=[rt_id], Tags=[{"Key": "Name", "Value": rt_name}])
    ec2.create_route(**create_params)

    print(f"Route Table {rt_name} with ID {rt_id} has been created successfully!")

    return rt_id


def create_subnet(vpc_id, cidr_block, az=None):
    subnet_name = f'subnet-{datetime.now().strftime("%Y%m%d%H%M%S")}'

    response = ec2.describe_subnets(
        Filters=[
            {"Name": "cidr-block", "Values": [cidr_block]}
        ]
    )
    subnets = response.get('Subnets', [])

    if subnets:
        subnet_id = subnets[0]['SubnetId']
        print(f"Subnet with CIDR {cidr_block} and ID {subnet_id} already exists.")

    create_params = {
        'VpcId': vpc_id,
        'CidrBlock': cidr_block
    }

    if az:
        create_params['AvailabilityZone'] = az

    subnet_response = ec2.create_subnet(**create_params)
    subnet_id = subnet_response['Subnet']['SubnetId']

    time.sleep(2)

    ec2.create_tags(Resources=[subnet_id], Tags=[{"Key": "Name", "Value": subnet_name}])

    print(f"Subnet {subnet_name} with ID {subnet_id} has been created successfully!")

    return subnet_id