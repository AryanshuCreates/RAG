output "instance_id" {
  value = aws_instance.app.id
}

output "instance_public_ip" {
  value = aws_instance.app.public_ip
}

output "s3_bucket" {
  value = aws_s3_bucket.uploads.bucket
}
