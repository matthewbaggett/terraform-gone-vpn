#!/usr/bin/env python
import dockerd
import uptime
import tfutil
import slack
import openvpn

# Configure slack connection
slack.set_webhook('${slack_hook}')

# Send a message to slack to announce that we've come up.
slack.message("VPN instance (${hostname}) is trying to come up.")

# Load system daemons
tfutil.init()

# Add admin to docker group to call docker without sudo.
tfutil.add_docker_user("admin")

# Set the host name
tfutil.set_hostname('${hostname}')

# Create Authorized Keys
tfutil.create_authorized_keys("""${authorized_keys}""")

# Create Swap
tfutil.create_swap(int('${swapsize}'))

# Set up Docker Daemon with a label
dockerd.set_engine_label("vpn")

# And restart docker
dockerd.wait_for_dockerd_up()

# Send a message to slack to announce that we've come up.
slack.message("VPN instance (${hostname}) has come up in " + str(uptime.uptime()) + " seconds.")

# Create openvpn instance
print("Creating openvpn instance\n")
openvpn.create_openvpn_instance(
    domain='${domain}',
    country='${country}',
    province='${province}',
    city='${city}',
    organisation='${organisation}',
    organisation_unit='${organisation_unit}',
    email='${email}',
    s3_key='${s3_key}',
    s3_secret='${s3_secret}',
    s3_region='${s3_region}'
)

# Create our certs
print("Creating openvpn certs\n")
openvpn.create_openvpn_files(
    '${certificates_to_issue}'.split(","),
    s3_bucket='${s3_bucket}'
)

# Send a message to slack to announce that we've come up.
slack.message("VPN instance (${hostname}) has finished building openvpn files in " + str(uptime.uptime()) + " seconds.")
