output "vpn_ip" {
  value = aws_eip.vpn.public_ip
}