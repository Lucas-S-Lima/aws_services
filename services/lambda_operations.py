import zipfile
import boto3
import time
import json

region = 'us-east-1'
lambda_name = f"my-bucket-{int(time.time())}"
region = 'us-east-1'
endpoint_url = 'http://localhost:4566'


lambda_client = boto3.client(
    'lambda',
    endpoint_url=endpoint_url,
    region_name=region,
)

def _create_zipped_file(source_file='services/main_lambda.py', arcname='main_lambda.py', zip_filename="function.zip"):
  with zipfile.ZipFile(zip_filename, 'w') as zipf:
    zipf.write(source_file, arcname=arcname)
  print(f"File '{zip_filename}' created.")


def create_lambda(name=lambda_name, source_file='services/main_lambda.py', handler='main_lambda.lambda_handler'):
  """
  Create a Lambda function from a local Python file.

  :param name: Name of the Lambda function
  :param source_file: Path to the Python source file (e.g. 'services/automating_ec2_snapshot.py')
  :param handler: Handler in the format 'module.function' (e.g. 'automating_ec2_snapshot.lambda_handler')
  """
  arcname = source_file.split('/')[-1]
  _create_zipped_file(source_file=source_file, arcname=arcname)
  with open("function.zip", "rb") as f:
    zipped_code = f.read()

  try:
    response = lambda_client.create_function(
        FunctionName=name,
        Runtime='python3.12',
        Role='arn:aws:iam::000000000000:role/lambda-role',
        Handler=handler,
        Code={'ZipFile': zipped_code},
        Description='Lambda created via localstack',
        Timeout=60,
        MemorySize=128,
    )
    print('Lambda created successfully')
    print(f"ARN: {response['FunctionArn']}")
  except Exception as e:
    print(f'Error: {e}')


def invoke_lambda(lambda_name):
  try:
    payload_data = {'mensagem': 'Olá do script Python!'}

    response = lambda_client.invoke(
        FunctionName=lambda_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload_data),
    )

    status_code = response['StatusCode']
    payload_retorno = response['Payload'].read().decode('utf-8')

    print(f'[INVOKE] Status HTTP: {status_code}')
    print(f'[INVOKE] Resposta da Lambda: {payload_retorno}')

  except Exception as e:
    print(f'[INVOKE] Erro ao invocar a Lambda: {e}')


def read_lambda(lambda_name):
  try:
    response = lambda_client.get_function(FunctionName=lambda_name)
    config = response['Configuration'] 
    print(f"[READ] Find config: {config['FunctionName']}")
    print(f"       Runtime: {config['Runtime']}")
    print(f"       Handler: {config['Handler']}")
  except Exception as e:
    print(f'Error: {e}')


def update_lambda(lambda_name):
  _create_zipped_file()
  with open('function.zip', 'rb') as f:
    zipped_code = f.read()

  try:
    response = lambda_client.update_function_code(FunctionName=lambda_name, ZipFile=zipped_code)
  except Exception as e:
    print(f'Error: {e}')


def delete_lambda(lambda_name):
  try:
    lambda_client.delete_function(FunctionName=lambda_name)
  except Exception as e:
    print(f'Error: {e}')

def update_lambda_env(lambda_name, env_vars):
  try:
    lambda_client.update_function_configuration(
        FunctionName=lambda_name,
        Environment={'Variables': env_vars},
    )
    print(f'Environment variables updated successfully for {lambda_name}.')
  except Exception as e:
    print(f'Error: {e}')