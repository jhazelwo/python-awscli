""" -*- coding: utf-8 -*- """
from python2awscli import bin_aws
from python2awscli.error import TooMany, MissingArgument
from python2awscli import must


class BaseSubnet(object):
    def __init__(self, name, region, vpc, cidr=None, zone=None):
        self.id = None
        self.name = name
        self.region = region
        self.vpc = vpc
        self.cidr = cidr  # Only optional if subnet already exists (lets User get CIDR by subnet Name)
        self.zone = zone  # [optional] Default: AWS selects one for you.
        if not self._get():
            self._create()

    def _get(self):
        command = ['ec2', 'describe-subnets', '--region', self.region,
                   '--filter',
                   'Name=vpc-id,Values={0}'.format(self.vpc),
                   ]
        if self.cidr:
            command.append('Name=cidrBlock,Values={0}'.format(self.cidr))  # Prefer to search by CIDR
        else:
            command.append('Name=tag:Name,Values={0}'.format(self.name))  # Else by name if User doesnt know the CIDR
        result = bin_aws(command)['Subnets']
        if not result:
            return False
        if len(result) > 1:
            raise TooMany('More than 1 result returned from command {0}'.format(command))
        print('Got {0}'.format(command))  # TODO: Log(...)
        self.id = result[0]['SubnetId']
        self.zone = result[0]['AvailabilityZone']
        self.cidr = result[0]['CidrBlock']
        return True

    def _create(self):
        if not self.cidr:
            raise MissingArgument('Subnet {0} not found and cannot create new one without cidr'.format(self.name))
        command = ['ec2', 'create-subnet', '--region', self.region,
                   '--vpc-id', self.vpc,
                   '--cidr-block', self.cidr,
                   ]
        if self.zone:
            command.append('--availability-zone')
            command.append(must.be_string(self.zone))
        result = bin_aws(command)
        print('Created {0}'.format(command))  # TODO: Log(...)
        self.id = result['Subnet']['SubnetId']
        command = ['ec2', 'create-tags',
                   '--region', self.region,
                   '--resources', self.id,
                   '--tags', 'Key=Name,Value={0}'.format(self.name)
                   ]
        bin_aws(command, decode_output=False)
        print('Named {0}'.format(command))  # TODO: Log(...)
        return True
