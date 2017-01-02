#!/usr/bin/env python3
""" -*- coding: utf-8 -*-
OK as of 05a48a96731d4ee544cdc9c262d04b5b56299816

This code shows how to:
    Set up a new VPC with 3 subnets.
    Create a NFS (EFS) mount available in those subnets
    Create a web load balancer, keypair, 1 running instance
    Create a small pgSQL RDS instance
    Create security groups for all resources to allow correct public, private and neighbor access.
    Create and attach a 1000gb data volume to the webserver instance.
    Create instances in the same tier across different availability zones

All methods check for existing resources before creation to prevent duplicates.

No methods currently exist that stop, destroy, delete or decommission resources.
    "Idempotent minus removal"
"""
from python2awscli.model import Instance, LoadBalancer, VPC, SecurityGroup, KeyPair, RDS, Volume, Subnet, EFS
from python2awscli.task import make_ipperms, make_listener


REGION = 'us-east-1'
IMAGE = 'ami-b7a114d7'  # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
EGRESS = {'Ipv6Ranges': [], 'PrefixListIds': [], 'IpRanges': [{'CidrIp': '0.0.0.0/0'}], 'UserIdGroupPairs': [],
          'IpProtocol': '-1'}  # This is the default egress rule for security groups


vpc_dev = VPC(name='DEV', region=REGION, cidr='10.10.0.0/16', ipv6=False)

my_subnet_a = Subnet(name='app-a', region=REGION, vpc=vpc_dev.id, cidr='10.10.1.0/24', zone='us-east-1a')
my_subnet_b = Subnet(name='app-b', region=REGION, vpc=vpc_dev.id, cidr='10.10.2.0/24', zone='us-east-1b')
my_subnet_c = Subnet(name='app-c', region=REGION, vpc=vpc_dev.id, cidr='10.10.3.0/24', zone='us-east-1c')

sg_nfs = SecurityGroup(name='nfs', region=REGION, vpc=vpc_dev.id,
                       description='NFS',
                       inbound=make_ipperms('{0}:2049/tcp'.format(vpc_dev.cidr)),
                       outbound=EGRESS)

mount = EFS(name='appservers:/app/etc', region=REGION, kind='maxIO',
            subnets=[my_subnet_a.id, my_subnet_b.id, my_subnet_c.id],
            groups=sg_nfs.id)

www_lb_sg = SecurityGroup(
    name='www',
    region=REGION,
    vpc=vpc_dev.id,
    description='Web Load Balancers',
    inbound=[
        make_ipperms('0.0.0.0/0:80/tcp'),
        make_ipperms('0.0.0.0/0:443/tcp'),
    ],
    outbound=EGRESS
)

TIER = 'webservers'
# Create
web_servers_key_pair = KeyPair('/aws/private', TIER, REGION)
web_server_security_group = SecurityGroup(
    name=TIER,
    region=REGION,
    vpc=vpc_dev.id,
    description='Web Server Instances',
    inbound=[
        make_ipperms('{0}/9876543210:80/tcp'.format(www_lb_sg.id)),  # LB
        make_ipperms('sg-b4b3000a/9876543210:22/tcp')                # jump servers
    ],
    outbound=EGRESS
)
# Create {count} number of instances, let AWS pick AZ
web_servers = Instance(
    name=TIER,
    region=REGION,
    vpc=vpc_dev.id,
    image=IMAGE,
    key=web_servers_key_pair.name,
    count=1,
    size='t2.micro',
    groups=web_server_security_group.id,
    public=True,
    script='/aws/private/webserver-post-install.sh'
)
# Create and attach a 1000gb EBS volume for each instance in web_servers
for this in web_servers.id:
    each = Volume(
        name='webserver-data', region=REGION, zone=web_servers.zone,
        kind='gp2', size='1000', instance=this, device='/dev/xvdd'
    )
# Standard LB with AWS-provided cert.
www_lb = LoadBalancer(
    name='www',
    region=REGION,
    listeners=[
        make_listener('80/http>80/http'),
        make_listener('443/https>80/http+us-east-1:9876543210:certificate/b4b3b4b3-b4b3-b4b3-b4b3b4b3'),
        ],
    zones=[
        'us-west-2a',
        'us-west-2b',
        'us-west-2c'
    ],
    groups=www_lb_sg.id,
    instances=web_servers.id
)
#
db_sg = SecurityGroup(
    name='db',
    region=REGION,
    vpc=vpc_dev.id,
    description='Databases',
    inbound={
        'FromPort': 5432,
        'IpProtocol': 'tcp',
        'IpRanges': [
            {'CidrIp': '8.8.8.8/32'},     # HOME
            {'CidrIp': '10.10.0.0/16'}],  # DEV VPC
        'Ipv6Ranges': [],
        'PrefixListIds': [],
        'ToPort': 5432,
        'UserIdGroupPairs': []
    },
    outbound=EGRESS
)
# A small pgSQL instance
my_db = RDS(
    name='oursql',
    region=REGION,
    engine='postgres',
    size='db.t2.micro',
    username='admin',
    password='Password123',
    gb=5,
    zone='us-west-2a',
    groups=[db_sg.id],
    public=True
)
# Create 1 server in each AZ
web_servers_a = Instance(
    name='webservers-az',
    region=REGION,
    vpc=vpc_dev.id,
    image=IMAGE,
    key=web_servers_key_pair.name,
    count=1,
    size='t2.micro',
    groups=web_server_security_group.id,
    public=True,
    script='/aws/private/user-data.sh',
    zone='us-west-2a',
)
web_servers_b = Instance(
    name='webservers-az',
    region=REGION,
    vpc=vpc_dev.id,
    image=IMAGE,
    key=web_servers_key_pair.name,
    count=1,
    size='t2.micro',
    groups=web_server_security_group.id,
    public=True,
    script='/aws/private/user-data.sh',
    zone='us-west-2b',
)
web_servers_c = Instance(
    name='webservers-az',
    region=REGION,
    vpc=vpc_dev.id,
    image=IMAGE,
    key=web_servers_key_pair.name,
    count=1,
    size='t2.micro',
    groups=web_server_security_group.id,
    public=True,
    script='/aws/private/user-data.sh',
    zone='us-west-2c',
)
