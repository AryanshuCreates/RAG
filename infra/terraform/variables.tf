variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "ssh_key_name" {
  description = "Name of an existing EC2 key pair to attach for SSH access (create in AWS console if needed)"
  type        = string
  default     = ""
}

variable "ami" {
  description = "AMI ID to use for the instance. If empty a default Amazon Linux 2 will be picked for the region."
  type        = string
  default     = ""
}

variable "s3_bucket_name" {
  description = "Name for the S3 bucket to store uploads/artifacts. Must be globally unique."
  type        = string
  default     = "rag-mvp-uploads-your-unique-suffix"
}

variable "allow_ssh_from" {
  description = "CIDR that is allowed to SSH into the EC2 instance (use your IP like 1.2.3.4/32)"
  type        = string
  default     = "0.0.0.0/0"
}

