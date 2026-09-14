import boto3
import time
import uuid

region = 'us-east-1'
rds = boto3.client('rds', region_name=region)

username = 'rootuser'
password = 'rootuserpassword123'
db_subnet_group = 'db-subnet-group'
db_cluster_id = f"db-id-{uuid.uuid4().hex[:8]}"
rds_database_name = f'database-{int(time.time())}'


def create_cluster():
    try:
        rds.create_db_cluster(
            Engine='aurora-postgresql',
            EngineVersion='15.4',
            DBClusterIdentifier=db_cluster_id,
            MasterUsername=username,
            MasterUserPassword=password,
            DatabaseName=rds_database_name,
            DBSubnetGroupName=db_subnet_group,
            EngineMode='serverless',
            EnableHttpEndpoint=True,
            ScalingConfiguration={
                'MinCapacity': 0.5,
                'MaxCapacity': 2,
                'AutoPause': True,
                'SecondsUntilAutoPause': 300,
            }
        )
        print(f"Cluster {db_cluster_id} creation started...")
        
        while True:
            response = rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
            status = response['DBClusters'][0]['Status']
            print(f"Cluster Status: {status}")
            if status == 'available':
                print("Your DB Cluster is available!")
                break
            time.sleep(15)
    except Exception as e:
        print(f"Error creating cluster: {e}")


def read_cluster():
    try:
        response = rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
        cluster = response['DBClusters'][0]
        print(f"--- Cluster Details ---")
        print(f"ID: {cluster['DBClusterIdentifier']}")
        print(f"Status: {cluster['Status']}")
        print(f"Engine: {cluster['Engine']} {cluster['EngineVersion']}")
        print(f"Endpoint: {cluster.get('Endpoint', 'N/A')}")
    except rds.exceptions.DBClusterNotFoundFault:
        print(f"Cluster {db_cluster_id} not found.")


def update_cluster():
    try:
        response = rds.modify_db_cluster(
            DBClusterIdentifier=db_cluster_id,
            ApplyImmediately=True,
            ScalingConfiguration={
                'MinCapacity': 0.5,
                'MaxCapacity': 4,
                'AutoPause': True,
                'SecondsUntilAutoPause': 600
            }
        )
        print(f"Cluster {db_cluster_id} update initiated.")
    except Exception as e:
        print(f"Error updating cluster: {e}")


def delete_cluster():
    try:
        rds.delete_db_cluster(
            DBClusterIdentifier=db_cluster_id,
            SkipFinalSnapshot=True
        )
        print(f"Cluster {db_cluster_id} deletion initiated.")
        
        while True:
            try:
                res = rds.describe_db_clusters(DBClusterIdentifier=db_cluster_id)
                print(f"Deletion status: {res['DBClusters'][0]['Status']}")
                time.sleep(15)
            except rds.exceptions.DBClusterNotFoundFault:
                print("Cluster successfully deleted.")
                break
    except Exception as e:
        print(f"Error deleting cluster: {e}")
