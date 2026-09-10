import boto3
import time
from botocore.exceptions import ClientError


bucket_name = f"my-bucket-{int(time.time())}"
region = 'us-east-1'

s3 = boto3.client('s3', region_name=region)


def create_bucket(bucket_name, bucket_region):
    """
    Create an S3 bucket in a specified region.

    :param bucket_name: Bucket to create
    :param bucket_region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """
    try:
        if bucket_region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': bucket_region}
            )
        print(f"Bucket {bucket_name} created successfully in {bucket_region}.")

    except ClientError as e:
        error_code = e.response['Error']['Code']

        if error_code == 'BucketAlreadyExists':
            raise ValueError(f"Bucket {bucket_name} already exists.")
        elif error_code == 'BucketAlreadyOwnedByYou':
            raise ValueError(f"Bucket {bucket_name} already owned by you.")
        else:
            raise Exception(f"Error creating bucket: {e}")


def create_file(bucket_name, file_name, content):
    """
    Create a file in the specified S3 bucket.

    :param bucket_name: Name of the bucket
    :param file_name: Name of the file to create
    :param content: Content to write to the file
    """

    with open(content, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=content)
        print(f"File {file_name} created successfully in bucket {bucket_name}.")
    except ClientError as e:
        raise Exception(f"Error creating file: {e}")


def update_file(bucket_name, file_name, new_content):
    """
    Update a file in the specified S3 bucket.

    :param bucket_name: Name of the bucket
    :param file_name: Name of the file to update
    :param new_content: New content to write to the file
    """
    with open(new_content, 'r', encoding='utf-8') as f:
        new_content = f.read()

    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=new_content)
        print(f"File {file_name} updated successfully in bucket {bucket_name}.")
    except ClientError as e:
        raise Exception(f"Error updating file: {e}")


def read_file(bucket_name, file_name):
    """
    Read a file from the specified S3 bucket.

    :param bucket_name: Name of the bucket
    :param file_name: Name of the file to read
    :return: Content of the file
    """
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        content = response['Body'].read().decode('utf-8')
        print(f"File {file_name} read successfully from bucket {bucket_name}.")
        return content
    except ClientError as e:
        raise Exception(f"Error reading file: {e}")


def delete_file(bucket_name, file_name):
    """
    Delete a file from the specified S3 bucket.

    :param bucket_name: Name of the bucket
    :param file_name: Name of the file to delete
    """
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
        print(f"File {file_name} deleted successfully from bucket {bucket_name}.")
    except ClientError as e:
        raise Exception(f"Error deleting file: {e}")


def delete_bucket(bucket_name):
    """
    Delete the specified S3 bucket.

    :param bucket_name: Name of the bucket to delete
    """
    try:
        s3.delete_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} deleted successfully.")
    except ClientError as e:
        raise Exception(f"Error deleting bucket: {e}")


def list_buckets():
    """
    List all S3 buckets.

    :return: List of bucket names
    """
    try:
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        print("Buckets listed successfully.")
        return buckets
    except ClientError as e:
        raise Exception(f"Error listing buckets: {e}")


def list_files(bucket_name):
    """
    List all files in the specified S3 bucket.

    :param bucket_name: Name of the bucket
    :return: List of file names
    """
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            files = [obj['Key'] for obj in response['Contents']]
            print(f"Files listed successfully in bucket {bucket_name}.")
            return files
        else:
            print(f"No files found in bucket {bucket_name}.")
            return []
    except ClientError as e:
        raise Exception(f"Error listing files: {e}")
