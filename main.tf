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

  tags = {
    Name = var.tag_name
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

  tags = {
    Name = var.tag_name
  }
}

resource "aws_eip" "vpn" {
  depends_on = [aws_instance.vpn]
  instance   = aws_instance.vpn.id
  vpc        = true
  tags = {
    Name = var.tag_name
  }
}

resource "aws_security_group" "vpn" {
  name   = "vpn"
  vpc_id = var.vpc_id

  tags = {
    "Name" = "VPN"
  }

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
    authorized_keys       = join("\n", var.ssh_authorized_keys)
    domain                = var.domain,
    country               = var.cert_country,
    province              = var.cert_province,
    city                  = var.cert_city,
    organisation          = var.cert_org
    organisation_unit     = var.cert_organisational_unit
    email                 = var.cert_email
    certificates_to_issue = join(",", var.certificates_to_issue)
  }
}

data "template_cloudinit_config" "vpn" {
  gzip          = "true"
  base64_encode = "true"

  part {
    content = file("${path.module}/common.cloud-config")
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
