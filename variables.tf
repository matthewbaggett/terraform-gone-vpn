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
  default     = ""
  type        = string
}

variable "cidr_block" {
  type        = string
  default     = "10.10.0.0/16"
  description = "Base IP address block you'd like your VPN to use for its AWS Security Group"
}

variable "cidr_block_offset" {
  type        = number
  default     = 255
  description = "What you'd like the 3rd octet of the IP CIDR block to be"
}

variable "tag_name" {
  description = "Default NAME tag resource in AWS"
  default     = "VPN"
}

variable "tags_extra" {
  description = "Extra tags you can use with AWS for resource tracking"
  default     = {}
  type        = map(string)
}

variable "domain" {
  type        = string
  default     = "vpn.in-a-can.local"
  description = "Domain to use for VPN"
}

variable "cert_country" {
  type        = string
  default     = "UK"
  description = "SSL Certificate Country"
}

variable "cert_province" {
  type    = string
  default = "Oxfordshire"

  description = "SSL Certificate Province"
}

variable "cert_city" {
  type        = string
  default     = "Oxford"
  description = "SSL Certificate City"
}

variable "cert_org" {
  type        = string
  default     = "Department of Defiance"
  description = "SSL Certificate Org"
}

variable "cert_organisational_unit" {
  type        = string
  default     = "Department of Defiance"
  description = "SSL Certificate OU"
}

variable "cert_email" {
  type        = string
  default     = "matthew@baggett.me"
  description = "SSL Certificate Email Address"
}

variable "certificates_to_issue" {
  type        = list(string)
  description = "VPN configuration files to generate users for (this is a list of names to generate matching name.ovpn files for)"
}

variable "s3_bucket_name" {}

variable "s3_bucket_user" {
  default = "vpn-s3-user"
}