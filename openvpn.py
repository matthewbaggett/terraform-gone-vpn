#!/usr/bin/env python
import docker, tarfile, io, subprocess


client = docker.from_env()

name = "openvpn"
image = "kylemanna/openvpn"
volumes = ["/tmp/purp:/etc/openvpn"]

always_delete_everything = False

def create_openvpn_instance(domain, country, province, city, organisation, organisation_unit, email, s3_key, s3_secret, s3_region):
    environment = [
        "EASYRSA_BATCH=yes",
        "EASYRSA_REQ_CN=" + domain,
        "EASYRSA_REQ_COUNTRY=" + country,
        "EASYRSA_REQ_PROVINCE=" + province,
        "EASYRSA_REQ_CITY=" + city,
        "EASYRSA_REQ_ORG=" + organisation,
        "EASYRSA_REQ_OU=" + organisation_unit,
        "EASYRSA_REQ_EMAIL=" + email,
    ]

    # Set up AWS
    subprocess.check_call(["aws", "configure", "set", "aws_access_key_id", s3_key])
    subprocess.check_call(["aws", "configure", "set", "aws_secret_access_key", s3_secret])

    # Remove this forceful baleetion
    if always_delete_everything:
        try:
            client.containers.get(name).stop()
            client.containers.get(name).remove()
            print "Terminated running instances, continuing"
        except docker.errors.NotFound as e:
            # Don't care, thats fine.
            print "No running instances, continuing"

    # If the named container doesn't exist, create it and our base PKI stuff
    instance = None
    try:
        instance = client.containers.get(name)
    except docker.errors.NotFound as e:
        print "Creating CA and base configuration"

        # Run the genconfig command
        print "Running genconfig"
        print client.containers.run(
            image=image,
            environment=environment,
            volumes=volumes,
            command="ovpn_genconfig -u udp://" + domain
        )

        # Run the ovpn_initpki command
        print "Running initpki"
        print client.containers.run(
            image=image,
            environment=environment,
            volumes=volumes,
            command="ovpn_initpki nopass"
        )

    # Incase the instance is exited, remove it.
    if instance is not None and instance.status == 'exited':
        client.containers.get(name).remove()

    # Run the persistent container
    if instance is None or instance.status != "running":
        print "Starting instance"
        instance = client.containers.run(
            name=name,
            image=image,
            detach=True,
            cap_add=["NET_ADMIN"],
            ports={'1194/udp':'1194'},
            restart_policy={"Name": "on-failure", "MaximumRetryCount": 0},
            volumes=volumes,
            nano_cpus=1000000000
        )
    else:
        print "Instance already started"

def create_openvpn_files(ovpn_files_to_generate, s3_bucket):
    instance = client.containers.get(name)

    # Generate user openvpn files
    for to_generate in ovpn_files_to_generate:
        print "Generating user \"" + to_generate + "\" openvpn files"
        instance.exec_run("easyrsa build-client-full " + to_generate + " nopass").output
        instance.exec_run("sh -c \"ovpn_getclient " + to_generate + " combined > /etc/openvpn/" + to_generate + ".ovpn\"").output

        bits, stat = instance.get_archive("/etc/openvpn/" + to_generate + ".ovpn")

        # Extract the key from the tarball we get from docker
        mp = io.BytesIO()
        for chunk in bits:
            mp.write(chunk)
        mp.seek(0)
        tar = tarfile.open(fileobj=mp)
        member = tar.getmembers()[0]
        content = tar.extractfile(member)

        # Write the extracted file into the local filesystem.
        ovpn_file = open(to_generate + ".ovpn", "w")
        ovpn_file.write(content.read())
        ovpn_file.close()
        tar.close()
        mp.close()
        print(" > File created: " + to_generate + ".ovpn")

        # Upload the keys to S3
        subprocess.check_call(["aws", "s3", "cp", to_generate + ".ovpn", "s3://" + s3_bucket + "/" + to_generate + ".ovpn"])
        print(" > Uploaded " + to_generate + ".ovpn to s3")

        # Delete evidence of the keys.
        instance.exec_run("rm /etc/openvpn/" + to_generate + ".ovpn")
        subprocess.check_call(["rm", to_generate + ".ovpn"])
