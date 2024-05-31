import pymysql
import boto3
from config import RDS_HOST, RDS_PORT, RDS_USER, RDS_DB, ENV
import logging
import config
import json

def get_secret_name(prefix):
    client = boto3.client('secretsmanager', region_name=config.RDS_REGION)
    try:
        # List secrets
        paginator = client.get_paginator('list_secrets')
        secrets = []
        for page in paginator.paginate():
            secrets.extend(page['SecretList'])
        
        # Filter secrets with the given prefix
        for secret in secrets:
            if secret['Name'].startswith(prefix):
                logging.info(f"Found secret: {secret['Name']}")
                return secret['Name']
    except Exception as e:
        logging.error(f"Error listing secrets: {e}")
        return None
    
    logging.error(f"No secret found with prefix {prefix}")
    return None

def get_secret(secret_name):
    # Create a Secrets Manager client
    client = boto3.client('secretsmanager', region_name=config.RDS_REGION)
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        logging.error(f"Error retrieving secret: {e}")
        return None

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

def find_rds_endpoint(prefix):
    client = boto3.client('rds', region_name=config.RDS_REGION)
    try:
        # List RDS instances
        paginator = client.get_paginator('describe_db_instances')
        instances = []
        for page in paginator.paginate():
            instances.extend(page['DBInstances'])
        
        # Filter instances with the given prefix
        for instance in instances:
            if instance['DBInstanceIdentifier'].startswith(prefix):
                endpoint = instance['Endpoint']['Address']
                logging.info(f"Found RDS endpoint: {endpoint}")
                return endpoint
    except Exception as e:
        logging.error(f"Error listing RDS instances: {e}")
        return None
    
    logging.error(f"No RDS instance found with prefix {prefix}")
    return None

def get_connection():
    if ENV == 'cloud':
        secret_name = get_secret_name('rds_password_')
        if not secret_name:
            logging.error("Failed to find secret with the specified prefix.")
            return None
        
        secret = get_secret(secret_name)
        if secret:
            password = secret['password']
        else:
            logging.error("Failed to retrieve secret from AWS Secrets Manager.")
            return None

        rds_host = find_rds_endpoint(RDS_HOST)
        if not rds_host:
            logging.error("Failed to find RDS endpoint with the specified prefix.")
            return None

        return pymysql.connect(
            host=rds_host,
            port=RDS_PORT,
            user=RDS_USER,
            password=password,
            database=RDS_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        return pymysql.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            user=RDS_USER,
            password=config.RDS_PASSWORD,
            database=RDS_DB,
            cursorclass=pymysql.cursors.DictCursor
        )

def create_tables():
    connection = get_connection()
    logging.info("Creating tables.")
    try:
        with connection.cursor() as cursor:
            logging.debug("Creating entries table")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    ticket_id VARCHAR(36) PRIMARY KEY,
                    plate VARCHAR(20),
                    parking_lot VARCHAR(10),
                    entry_time DATETIME,
                    exit_time DATETIME DEFAULT NULL,
                    charge DECIMAL(10, 2) DEFAULT NULL,
                    deletedAt DATETIME DEFAULT NULL
                )""")
        connection.commit()
    except:
        logging.error("Failed creating Tables")
    finally:
        connection.close()
