data "aws_ami" "base_ami" {
  most_recent = true
  name_regex  = var.base_ami_regexp
  owners      = ["amazon", "self"]
}

resource "aws_instance" "vpn" {
  depends_on             = [aws_security_group.vpn]
  ami                    = data.aws_ami.base_ami.id
  instance_type          = var.instance_type
  user_data_base64       = data.template_cloudinit_config.vpn.rendered
  monitoring             = false
  subnet_id              = aws_subnet.vpn.id
  vpc_security_group_ids = [aws_security_group.vpn.id]

  tags = merge(map("Name", var.tag_name), var.tags_extra)

  lifecycle {
    create_before_destroy = true
  }

  root_block_device {
    volume_size = 8
  }

  credit_specification {
    cpu_credits = "standard"
  }
}

resource "aws_subnet" "vpn" {
  vpc_id                  = var.vpc_id
  cidr_block              = cidrsubnet(var.cidr_block, 8, var.cidr_block_offset, )
  map_public_ip_on_launch = true

  tags = merge(map("Name", var.tag_name), var.tags_extra)
}

resource "aws_eip" "vpn" {
  depends_on = [aws_instance.vpn]
  instance   = aws_instance.vpn.id
  vpc        = true
  tags       = merge(map("Name", var.tag_name), var.tags_extra)
}

resource "aws_s3_bucket" "vpn_bucket" {
  bucket = var.s3_bucket_name
  acl    = "private"
  tags   = merge(map("Name", var.tag_name), var.tags_extra)
}

resource "aws_s3_bucket_public_access_block" "vpn_bucket" {
  bucket = aws_s3_bucket.vpn_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_user" "vpn_bucket" {
  name = var.s3_bucket_user
}

resource "aws_iam_access_key" "vpn_bucket" {
  user = aws_iam_user.vpn_bucket.name
}

resource "aws_iam_user_policy_attachment" "attach-s3-vpn_bucket" {
  user = aws_iam_user.vpn_bucket.name
  # @todo Revise this policy, it doesn't really need full access to S3.
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

output "vpn_bucket_user" {
  value = aws_iam_user.vpn_bucket.name
}
output "vpn_bucket_key" {
  value = aws_iam_access_key.vpn_bucket.id
}
output "vpn_bucket_secret" {
  value = aws_iam_access_key.vpn_bucket.secret
}
output "vpn_bucket" {
  value = aws_s3_bucket.vpn_bucket.id
}

resource "aws_security_group" "vpn" {
  name   = "vpn"
  vpc_id = var.vpc_id

  tags = merge(map("Name", var.tag_name), var.tags_extra)

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    self        = true
  }

  ingress {
    from_port   = 1194
    to_port     = 1194
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "template_file" "vpn" {
  template = file("${path.module}/vpn.py")

  vars = {
    hostname              = var.hostname,
    slack_hook            = var.slack-hook,
    swapsize              = 1,
    authorized_keys       = var.ssh_authorized_keys
    domain                = var.domain,
    country               = var.cert_country,
    province              = var.cert_province,
    city                  = var.cert_city,
    organisation          = var.cert_org
    organisation_unit     = var.cert_organisational_unit
    email                 = var.cert_email
    certificates_to_issue = join(",", var.certificates_to_issue)
    s3_region             = data.aws_region.current.name
    s3_key                = aws_iam_access_key.vpn_bucket.id
    s3_secret             = aws_iam_access_key.vpn_bucket.secret
    s3_bucket             = aws_s3_bucket.vpn_bucket.id
  }
}

data "aws_region" "current" {}

data "template_cloudinit_config" "vpn" {
  gzip          = "true"
  base64_encode = "true"

  part {
    content = file("${path.module}/cloud-config.yaml")
  }

  part {
    filename = "dockerd.py"
    content  = file("${path.module}/dockerd.py")
  }

  part {
    filename = "openvpn.py"
    content  = file("${path.module}/openvpn.py")
  }

  part {
    filename = "slack.py"
    content  = file("${path.module}/slack.py")
  }

  part {
    filename = "tfutil.py"
    content  = file("${path.module}/tfutil.py")
  }

  part {
    filename = "uptime.py"
    content  = file("${path.module}/uptime.py")
  }

  part {
    filename     = "vpn.py"
    content      = data.template_file.vpn.rendered
    content_type = "text/x-shellscript"
  }
}
