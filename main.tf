provider "aws" {
  region = "us-east-1"
}

# Create VPC
resource "aws_vpc" "main_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "main-vpc"
  }
}

# Create Subnets in two different AZs
resource "aws_subnet" "main_subnet_a" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "us-east-1a"
  tags = {
    Name = "main-subnet-a"
  }
}

resource "aws_subnet" "main_subnet_b" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  tags = {
    Name = "main-subnet-b"
  }
}

# Create Internet Gateway
resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name = "main-igw"
  }
}

# Create Route Table
resource "aws_route_table" "main_rt" {
  vpc_id = aws_vpc.main_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
  tags = {
    Name = "main-rt"
  }
}

# Associate Route Table with Subnets
resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.main_subnet_a.id
  route_table_id = aws_route_table.main_rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.main_subnet_b.id
  route_table_id = aws_route_table.main_rt.id
}

# Create Security Group
resource "aws_security_group" "app_sg" {
  vpc_id      = aws_vpc.main_vpc.id
  name        = "app-security-group"
  description = "Allow inbound traffic for app and database"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "main-subnet-group"
  subnet_ids = [aws_subnet.main_subnet_a.id, aws_subnet.main_subnet_b.id]

  tags = {
    Name = "main-subnet-group"
  }
}

# Generate a random password
resource "random_password" "rds_password" {
  length  = 16
  special = false
}

# Generate a random suffix for the secret name
resource "random_id" "secret_suffix" {
  byte_length = 8
}

# Store the password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "rds_secret" {
  name = "rds_password_${random_id.secret_suffix.hex}"
}

resource "aws_secretsmanager_secret_version" "rds_secret_version" {
  secret_id = aws_secretsmanager_secret.rds_secret.id
  secret_string = jsonencode({
    username = "admin"
    password = random_password.rds_password.result
  })
}

# Create RDS instance
resource "aws_db_instance" "default" {
  allocated_storage    = 10
  engine               = "mysql"
  instance_class       = "db.t3.micro"
  db_name              = "parking_lot_db"
  username             = "db_user"
  password             = random_password.rds_password.result
  db_subnet_group_name = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  identifier          = "app-instance-db"
  iam_database_authentication_enabled = true

  skip_final_snapshot = true
}

resource "aws_iam_role" "ec2_role" {
  name = "hw1-rds-role-ec2"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  inline_policy {
    name   = "rds-policy"
    policy = data.aws_iam_policy_document.rds_policy.json
  }
}

data "aws_iam_policy_document" "rds_policy" {
  statement {
    actions   = ["rds:*", "secretsmanager:GetSecretValue", "rds-db:connect", "secretsmanager:GetSecretValue", "secretsmanager:ListSecrets"]
    resources = ["*"]
  }
}

resource "local_file" "deploy_script" {
  filename = "deploy.sh"
  content  = file("deploy.sh")
}

resource "aws_instance" "app_instance" {
  ami                    = "ami-00beae93a2d981137"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.main_subnet_a.id
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name
  associate_public_ip_address = true
  key_name               = "moshiko_keys"  # Ensure this matches the name of your key pair in AWS

  user_data = local_file.deploy_script.content
  depends_on = [aws_db_instance.default]
  tags = {
    Name = "AppInstance"
  }
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-profile"
  role = aws_iam_role.ec2_role.name
}
