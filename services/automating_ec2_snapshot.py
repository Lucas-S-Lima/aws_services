import json
import os
import boto3
import logging
from datetime import datetime

log = logging.getLogger()
log.setLevel(logging.INFO)

INSTANCE_ID = os.environ.get('INSTANCE_ID', '')
VOLUME_ID = os.environ.get('VOLUME_ID', '')
SNAPSHOT_TAG_PREFIX = os.environ.get('SNAPSHOT_TAG_PREFIX', 'ec2-snapshot')


def _get_volume_ids_from_instance(ec2_client, instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    reservations = response.get('Reservations', [])

    if not reservations:
        raise ValueError(f"No instance found with ID: {instance_id}")

    volume_ids = []
    for reservation in reservations:
        for instance in reservation.get('Instances', []):
            for mapping in instance.get('BlockDeviceMappings', []):
                vol_id = mapping.get('Ebs', {}).get('VolumeId')
                if vol_id:
                    volume_ids.append(vol_id)

    if not volume_ids:
        raise ValueError(f"No EBS volumes found for instance: {instance_id}")

    return volume_ids


def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    created_snapshots = []
    errors = []

    try:
        if INSTANCE_ID:
            log.info(f"Fetching volumes for instance: {INSTANCE_ID}")
            volume_ids = _get_volume_ids_from_instance(ec2, INSTANCE_ID)
            log.info(f"Volumes found: {volume_ids}")
        elif VOLUME_ID:
            volume_ids = [VOLUME_ID]
            log.info(f"Using directly configured volume: {VOLUME_ID}")
        else:
            raise ValueError(
                "No volume source configured. "
                "Set INSTANCE_ID or VOLUME_ID in the Lambda environment variables."
            )

        for vol_id in volume_ids:
            try:
                response = ec2.create_snapshot(
                    VolumeId=vol_id,
                    Description=f"{SNAPSHOT_TAG_PREFIX}-{current_datetime}",
                    TagSpecifications=[
                        {
                            'ResourceType': 'snapshot',
                            'Tags': [
                                {'Key': 'Name', 'Value': f"{SNAPSHOT_TAG_PREFIX}-{current_datetime}"},
                                {'Key': 'VolumeId', 'Value': vol_id},
                                {'Key': 'CreatedBy', 'Value': 'Lambda-AutoSnapshot'},
                                {'Key': 'InstanceId', 'Value': INSTANCE_ID or 'N/A'},
                            ],
                        }
                    ],
                )
                snapshot_id = response['SnapshotId']
                created_snapshots.append(snapshot_id)
                log.info(f"Snapshot created successfully: {snapshot_id} (volume: {vol_id})")

            except Exception as e:
                err_msg = f"Failed to create snapshot for volume {vol_id}: {str(e)}"
                log.error(err_msg)
                errors.append(err_msg)

    except Exception as e:
        log.error(f"Fatal error in Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
        }

    body = {
        'message': f"{len(created_snapshots)} snapshot(s) created successfully.",
        'snapshots': created_snapshots,
    }

    if errors:
        body['errors'] = errors

    status_code = 200 if created_snapshots else 500
    return {'statusCode': status_code, 'body': json.dumps(body, default=str)}

