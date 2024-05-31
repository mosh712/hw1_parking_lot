import os

# Determine environment
ENV = os.getenv('ENV', 'local')  # Default to 'local' if not set

# Common configuration
RDS_DB = os.getenv('RDS_DB', 'parking_lot_db')
RDS_PORT = 3306

# Environment-specific configuration
if ENV == 'cloud':
    RDS_HOST = os.getenv('RDS_HOST', "hw1-database.cpe6w08wm4oa.us-east-1.rds.amazonaws.com")
    RDS_USER = os.getenv('RDS_USER', 'admin')  # IAM authenticated user
    RDS_REGION = os.getenv('RDS_REGION', 'us-east-1')
else:
    RDS_HOST = os.getenv('RDS_HOST', 'localhost')
    RDS_USER = os.getenv('RDS_USER', 'admin')
    RDS_PASSWORD = os.getenv('RDS_PASSWORD', '')
