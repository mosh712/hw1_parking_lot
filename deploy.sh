#!/bin/bash

# Update and install dependencies
sudo yum update && yum upgrade -y
sudo yum install -y python3-pip
sudo yum install -y git
git clone https://github.com/mosh712/hw1_parking_lot.git
cd hw1_parking_lot

pip3 install -r requirements.txt

# Export environment variables
export ENV="cloud"
export RDS_HOST="app-instance-db"
export RDS_USER="db_user"
export RDS_DB="parking_lot_db"
export RDS_REGION="us-east-1"

# Run the Flask application
python3 app.py
