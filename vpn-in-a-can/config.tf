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

variable "domain" {
  type    = string
  default = "vpn.in-a-can.local"
}

variable "cert_country" {
  type    = string
  default = "UK"
}

variable "cert_province" {
  type    = string
  default = "Oxfordshire"
}

variable "cert_city" {
  type    = string
  default = "Oxford"
}

variable "cert_org" {
  type    = string
  default = "Department of Defiance"
}

variable "cert_organisational_unit" {
  type    = string
  default = "Department of Defiance"
}

variable "cert_email" {
  type    = string
  default = "matthew@baggett.me"
}

variable "certificates_to_issue" {
  type = list(string)
}