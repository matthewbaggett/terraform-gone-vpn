provider "aws" {
  alias   = "my-aws-instance"
  version = "~> 2.30"
  profile = "default"
  region  = "eu-west-3"
}

module "vpn" {
  source  = "matthewbaggett/vpn/gone"
  version = ">=0.1.0"

  providers = {
    aws = aws.my-aws-instance
  }

  vpc_id                = "your-vpc-id"
  instance_type         = "t3a.nano"
  ssh_authorized_keys   = [file("~/.ssh/id_rsa.pub")]
  certificates_to_issue = ["tom", "dick", "harry"]
  #slack-hook           = "https://hooks.slack.com/services/THIS_IS_A_SECRET"
}

output "vpn_ip" {
  value = module.vpn.vpn_ip
}

