# --- Data: pick AMI if not provided ---
data "aws_ami" "amazon_linux2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# --- Security group ---
resource "aws_security_group" "rag_sg" {
  name        = "rag-mvp-sg"
  description = "Allow HTTP and SSH"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allow_ssh_from]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rag-mvp-sg"
  }
}

# --- VPC data to pick default VPC (common in accounts) ---
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "default" {
  vpc_id = data.aws_vpc.default.id
}

# --- EC2 instance ---
resource "aws_instance" "app" {
  ami           = var.ami != "" ? var.ami : data.aws_ami.amazon_linux2.id
  instance_type = var.instance_type
  subnet_id     = length(data.aws_subnet_ids.default.ids) > 0 ? data.aws_subnet_ids.default.ids[0] : null
  vpc_security_group_ids = [aws_security_group.rag_sg.id]

  # Optional SSH key pair
  key_name = var.ssh_key_name != "" ? var.ssh_key_name : null

  tags = {
    Name = "rag-mvp-instance"
  }

  # Basic userdata: install docker and docker-compose (you may expand this)
  user_data = <<-EOF
              #!/bin/bash
              set -e
              yum update -y
              amazon-linux-extras install docker -y || yum install -y docker
              service docker start
              usermod -a -G docker ec2-user
              curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              EOF
}

# --- S3 bucket for uploads/artifacts ---
resource "aws_s3_bucket" "uploads" {
  bucket = var.s3_bucket_name
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name = "rag-mvp-uploads"
  }
}

output "instance_id" {
  value = aws_instance.app.id
}

output "instance_public_ip" {
  value = aws_instance.app.public_ip
}

output "s3_bucket" {
  value = aws_s3_bucket.uploads.bucket
}
