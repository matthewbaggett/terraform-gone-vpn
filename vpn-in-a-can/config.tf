variable "vpc_id" {
  type        = string
  description = "Your VPC ID"
}

variable "base_ami_regexp" {
  default = "amzn2-ami-hvm-2.0.20190823.1-x86_64-ebs"
  type    = string
}

variable "instance_type" {
  default     = "t3.nano"
  description = "Type of instance to use"
}

variable "hostname" {
  default     = "vpn"
  description = "Hostname for the vpn machine"
}

variable "slack-hook" {
  default     = ""
  description = "Put a slack webhook here if you'd like a message when the VPN comes up..."
}

variable "ssh_authorized_keys" {
  description = "Default keys to put in authorized_keys"
  default     = []
  type        = list(string)
}

variable "cidr_block" {
  type    = string
  default = "10.10.0.0/16"
}

variable "cidr_block_offset" {
  type    = number
  default = 255
}

variable "tag_name" {
  description = "Default NAME tag resource in AWS"
  default     = "VPN"
}