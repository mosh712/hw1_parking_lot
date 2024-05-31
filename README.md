# Parking Lot Management System

The Parking Lot Management System is a web application designed to manage vehicle entries and exits in a parking lot. It is built using Flask for the web framework and MySQL for the database, with AWS services for deployment and credential management.

## Overview

The system allows for efficient management of vehicle entries and exits, storing the data in an AWS RDS MySQL database. The application is deployed on AWS EC2 instances, with credentials securely managed via AWS Secrets Manager.

## Architecture

- **Backend**: Flask
- **Database**: MySQL (AWS RDS)
- **Hosting**: AWS EC2
- **Credential Management**: AWS Secrets Manager
- **Infrastructure Management**: Terraform

## Features

- Record vehicle entry
- Record vehicle exit
- Secure credential management with AWS Secrets Manager
- Automated infrastructure setup with Terraform
- Deployed on AWS EC2

## Prerequisites

- Python 3.x
- AWS CLI configured with appropriate permissions with AWS account
- Terraform
- Git

## Installation

1. Execute `terraform init`
2. Execute `terraform apply`
