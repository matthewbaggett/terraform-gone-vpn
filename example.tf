provider "aws" {
  alias   = "my-aws-instance"
  version = "~> 2.30"
  profile = "default"
  region  = "us-east-1"
}

module "vpn-in-a-can" {
  source = "./vpn-in-a-can"

  providers = {
    aws = aws.my-aws-instance
  }

  vpc_id              = "your-vpc-id"
  instance_type       = "t3a.nano"
  ssh_authorized_keys = [file("~/.ssh/id_rsa.pub")]
}

output "vpn_ip" {
  value = module.vpn-in-a-can.vpn_ip
}

