import os
import boto3
import botocore.exceptions
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

instance_name = f'my-ec2-instance-{datetime.now().strftime("%Y%m%d%H%M%S")}'
region = 'us-east-1'
endpoint_url = 'http://localhost:4566'
key_name = os.getenv('KEY_NAME', 'default')

session = boto3.Session(profile_name="localstack")
ec2 = session.resource('ec2', region_name=region, endpoint_url=endpoint_url)


def get_latest_amzn2_ami(region_name):
    """Return the latest Amazon Linux 2 AMI ID from SSM Parameter Store for the region."""

    ssm = boto3.client('ssm', region_name=region_name)
    param_name = '/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
    resp = ssm.get_parameter(Name=param_name)

    return resp['Parameter']['Value']


def create_ec2_instance(instance_name=instance_name, image_id=None):
    """
    Create an EC2 instance with the specified name.

    :param instance_name: Name of the EC2 instance to create
    :return: Instance ID of the created or existing instance
    """
    all_instances = ec2.instances.all()
    existing_instance = False

    for instance in all_instances:
        if not instance.tags:
            continue
        for tag in instance.tags:
            if tag.get('Key') == 'Name' and tag.get('Value') == instance_name:
                existing_instance = True
                instance_id = instance.id
                print(f"Instance {instance_name} already exists with the instance ID: {instance_id}")
                break
        if existing_instance:
            break

    if not existing_instance:
        if image_id is None:
            try:
                image_id = get_latest_amzn2_ami(region)
            except botocore.exceptions.ClientError as e:
                print(f"Failed to look up default AMI in region {region}: {e}")
                raise

        try:
            new_instance = ec2.create_instances(
                ImageId=image_id,
                MinCount=1,
                MaxCount=1,
                InstanceType='t3.micro',
                KeyName='ec2-aws-key',  
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        }
                    ]
                }
            ]
        )
        except botocore.exceptions.ClientError as e:
            print(f"Failed to create instance (ClientError): {e}")
            raise

        instance_id = new_instance[0].id
        print(f"Instance {instance_name} created successfully with the instance ID: {instance_id}")

    return instance_id


def stop_ec2_instance(instance_id):
    """
    Stop the specified EC2 instance.

    :param instance_id: ID of the EC2 instance to stop
    """
    instance = ec2.Instance(instance_id)
    instance.stop()
    print(f"Instance {instance_id} stopped successfully.")


def start_ec2_instance(instance_id):
    """
    Start the specified EC2 instance.

    :param instance_id: ID of the EC2 instance to start
    """
    instance = ec2.Instance(instance_id)
    instance.start()
    print(f"Instance {instance_id} started successfully.")


def terminate_ec2_instance(instance_id):
    """
    Terminate the specified EC2 instance.

    :param instance_id: ID of the EC2 instance to terminate
    """
    instance = ec2.Instance(instance_id)
    instance.terminate()
    print(f"Instance {instance_id} terminated successfully.")