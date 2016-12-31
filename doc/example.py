#!/usr/bin/env python3
""" -*- coding: utf-8 -*-
This example OK as of cea59e92a2e53167715e2516cb6583cec4e7e12e
"""
exit()

from python2awscli.model import Instance, LoadBalancer, VPC, SecurityGroup, KeyPair, RDS, Volume, Subnet, EFS
from python2awscli.task import make_ipperms, make_listener


REGION = 'us-east-1'

# By default all new SGs are allowed to send anything to anyone.
EGRESS = {'Ipv6Ranges': [], 'PrefixListIds': [], 'IpRanges': [{'CidrIp': '0.0.0.0/0'}], 'UserIdGroupPairs': [],
          'IpProtocol': '-1'}

vpc_dev = VPC(name='DEV', region=REGION, cidr='10.10.0.0/16', ipv6=False)

my_subnet_a = Subnet(name='app-a', region=REGION, vpc=vpc_dev.id, cidr='10.10.1.0/24', zone='us-west-2a')
my_subnet_b = Subnet(name='app-b', region=REGION, vpc=vpc_dev.id, cidr='10.10.2.0/24', zone='us-west-2b')
my_subnet_c = Subnet(name='app-c', region=REGION, vpc=vpc_dev.id, cidr='10.10.3.0/24', zone='us-west-2c')


sg_nfs = SecurityGroup(name='nfs', region=REGION, vpc=vpc_dev.id,
                       description='NFS',
                       inbound=make_ipperms('{0}:2049/tcp'.format(vpc_dev.cidr)),
                       outbound=EGRESS)

mount = EFS(name='appservers:/app/etc', region=REGION, kind='maxIO',
            subnets=[my_subnet_a.id, my_subnet_b.id, my_subnet_c.id],
            groups=sg_nfs.id)

vpc_prod = VPC(
    name='PRODUCTION',
    region=REGION,
    cidr='10.4.0.0/16',
    ipv6=False,
)
www_lb_sg = SecurityGroup(
    name='www',
    region=REGION,
    vpc=vpc_prod.id,
    description='Web Load Balancers',
    inbound=[
        make_ipperms('0.0.0.0/0:80/tcp'),
        make_ipperms('0.0.0.0/0:443/tcp'),
    ],
    outbound=EGRESS
)

TIER = 'webservers'
web_servers_key_pair = KeyPair('/aws/private', TIER, REGION)
web_server_security_group = SecurityGroup(
    name=TIER,
    region=REGION,
    vpc=vpc_prod.id,
    description='Web Server Instances',
    inbound=[
        make_ipperms('{0}/9876543210:80/tcp'.format(www_lb_sg.id)),  # LB
        make_ipperms('sg-b4b3000a/9876543210:22/tcp')                # jump servers
    ],
    outbound=EGRESS
)
web_servers = Instance(
    name=TIER,
    region=REGION,
    vpc=vpc_prod.id,
    image='ami-b7a114d7',  # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
    key=web_servers_key_pair.name,
    count=1,
    size='t2.micro',
    groups=web_server_security_group.id,
    public=True,
    script='/aws/private/webserver-post-install.sh'
)

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

db_sg = SecurityGroup(
    name='db',
    region=REGION,
    vpc=vpc_prod.id,
    description='Databases',
    inbound={
        'FromPort': 5432,
        'IpProtocol': 'tcp',
        'IpRanges': [
            {'CidrIp': '8.8.8.8/32'},    # HOME
            {'CidrIp': '10.4.0.0/16'}],  # PRODUCTION VPC
        'Ipv6Ranges': [],
        'PrefixListIds': [],
        'ToPort': 5432,
        'UserIdGroupPairs': []
    },
    outbound=EGRESS
)
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
for this in web_servers.id:
    each = Volume(
        name='webserver-data', region=REGION, zone=web_servers.zone,
        kind='gp2', size='1000', instance=this, device='/dev/xvdd'
    )
