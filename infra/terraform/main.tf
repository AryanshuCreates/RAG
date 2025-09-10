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
  description = "Allow HTTP (frontend) and SSH"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP for frontend"
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

# --- VPC/Subnet ---
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet_ids" "default" {
  vpc_id = data.aws_vpc.default.id
}

# --- EBS volume ---
resource "aws_ebs_volume" "chroma_data" {
  availability_zone = element(data.aws_subnet_ids.default.ids, 0)
  size              = 20 # GB (adjust as needed)
  type              = "gp3"

  tags = {
    Name = "chroma-data-volume"
  }
}

# --- EC2 instance ---
resource "aws_instance" "app" {
  ami                    = var.ami != "" ? var.ami : data.aws_ami.amazon_linux2.id
  instance_type          = var.instance_type
  subnet_id              = length(data.aws_subnet_ids.default.ids) > 0 ? data.aws_subnet_ids.default.ids[0] : null
  vpc_security_group_ids = [aws_security_group.rag_sg.id]

  # Optional SSH key pair
  key_name = var.ssh_key_name != "" ? var.ssh_key_name : null

  tags = {
    Name = "rag-mvp-instance"
  }

  # Attach EBS volume
  ebs_block_device {
    device_name = "/dev/xvdf"
    volume_id   = aws_ebs_volume.chroma_data.id
  }

  # Userdata: install docker, mount EBS, deploy app
  user_data = <<-EOF
              #!/bin/bash
              set -e
              yum update -y
              amazon-linux-extras install docker -y || yum install -y docker
              service docker start
              usermod -a -G docker ec2-user

              # Install docker-compose
              curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose

              # Mount EBS volume for Chroma persistence
              mkfs -t xfs /dev/xvdf
              mkdir -p /data/chroma
              mount /dev/xvdf /data/chroma
              echo "/dev/xvdf /data/chroma xfs defaults,nofail 0 2" >> /etc/fstab

              # Clone repo and deploy
              cd /home/ec2-user
              git clone https://github.com/your/repo.git rag-app
              cd rag-app
              docker-compose up -d
              EOF
}
