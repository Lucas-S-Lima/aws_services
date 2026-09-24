import boto3
from botocore.exceptions import ClientError


region = 'us-east-1'
endpoint_url = 'http://localhost:4566'

session = boto3.Session(profile_name="localstack")
events = session.client('events', region_name=region, endpoint_url=endpoint_url)


def create_rule(rule_name, schedule_expression, description=''):
    try:
        response = events.put_rule(
            Name=rule_name,
            ScheduleExpression=schedule_expression,
            State='ENABLED',
            Description=description,
        )
        print(f"Rule '{rule_name}' created successfully.")
        return response['RuleArn']
    except ClientError as e:
        raise Exception(f"Error creating rule: {e}")


def read_rule(rule_name):
    try:
        response = events.describe_rule(Name=rule_name)
        print(f"[READ] Rule: {response['Name']}")
        print(f"       Schedule: {response.get('ScheduleExpression', 'N/A')}")
        print(f"       State: {response['State']}")
        return response
    except ClientError as e:
        raise Exception(f"Error reading rule: {e}")


def update_rule(rule_name, schedule_expression, description=''):
    try:
        response = events.put_rule(
            Name=rule_name,
            ScheduleExpression=schedule_expression,
            State='ENABLED',
            Description=description,
        )
        print(f"Rule '{rule_name}' updated successfully.")
        return response['RuleArn']
    except ClientError as e:
        raise Exception(f"Error updating rule: {e}")


def delete_rule(rule_name):
    try:
        targets = events.list_targets_by_rule(Rule=rule_name).get('Targets', [])
        if targets:
            target_ids = [t['Id'] for t in targets]
            events.remove_targets(Rule=rule_name, Ids=target_ids)
        events.delete_rule(Name=rule_name)
        print(f"Rule '{rule_name}' deleted successfully.")
    except ClientError as e:
        raise Exception(f"Error deleting rule: {e}")


def list_rules(name_prefix=''):
    try:
        kwargs = {'NamePrefix': name_prefix} if name_prefix else {}
        response = events.list_rules(**kwargs)
        rules = response.get('Rules', [])
        print(f"{len(rules)} rule(s) found.")
        for rule in rules:
            print(f"  - {rule['Name']} | {rule.get('ScheduleExpression', 'N/A')} | {rule['State']}")
        return rules
    except ClientError as e:
        raise Exception(f"Error listing rules: {e}")
''

def add_target(rule_name, target_id, target_arn):
    try:
        events.put_targets(
            Rule=rule_name,
            Targets=[{'Id': target_id, 'Arn': target_arn}],
        )
        print(f"Target '{target_id}' added to rule '{rule_name}' successfully.")
    except ClientError as e:
        raise Exception(f"Error adding target: {e}")


def remove_target(rule_name, target_id):
    try:
        events.remove_targets(Rule=rule_name, Ids=[target_id])
        print(f"Target '{target_id}' removed from rule '{rule_name}' successfully.")
    except ClientError as e:
        raise Exception(f"Error removing target: {e}")