# python-awscli
* Provides a Python3 layer to AWS's CLI, all wrapped in a Docker
container
* This projects exists mostly just for fun
* There is almost no input checking. Trust is implicit as anyone who
can run this code already has full access to the bin/aws program. We
let AWS's code and permission structure do the real work.

## Usage
* Full examples in [doc/example.py](https://github.com/jhazelwo/python-awscli/blob/master/doc/example.py)
* Some brief examples:

```python
vpc_dev = VPC(name='DEV', region='us-east-1', cidr='10.10.0.0/16', ipv6=False)

my_subnet_a = Subnet(name='www-a', region='us-east-1', vpc=vpc_dev.id, cidr='10.10.1.0/24', zone='us-east-1a')

web_servers_key_pair = KeyPair('/aws/private', 'webservers', 'us-east-1')

web_servers = Instance(
    name='webservers',
    region='us-east-1',
    vpc=vpc_dev.id,
    image='ami-b7a114d7',  # Ubuntu Server 16.04 LTS (HVM), SSD Volume Type
    key=web_servers_key_pair.name,
    count=1,
    size='t2.micro',
    groups=web_server_security_group.id,
    public=True,
    script='/aws/private/webserver-post-install.sh'
)

for this in web_servers.id:
    each = Volume(
        name='webserver-data', region=REGION, zone=web_servers.zone,
        kind='gp2', size='1000', instance=this, device='/dev/xvdd'
    )
```

## TODO
* Casual code clean-ups
