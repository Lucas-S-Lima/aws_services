import json


def lambda_handler(event, context):
  print('Lambda executada com sucesso!')
  return {'statusCode': 200, 'body': json.dumps('Hello World, Lambda!')}