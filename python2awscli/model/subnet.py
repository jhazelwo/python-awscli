""" -*- coding: utf-8 -*- """
from pprint import pprint

from python2awscli import bin_aws
from python2awscli.error import TooMany
from python2awscli import must


class BaseSubnet(object):
    def __init__(self, name, region, vpc, cidr, zone=None):
        self.id = None
        self.name = name
        self.region = region
        self.vpc = vpc
        self.cidr = cidr
        self.zone = zone  # [optional] Default: AWS selects one for you.
        if not self._get():
            self._create()

    def _get(self):
        """ describe-subnets
        [--subnet-ids <value>]
        [--filters <value>]
            o availabilityZone  -  The Availability Zone for the subnet. You can also use availability-zone as the
                filter name.
            o available-ip-address-count - The number of IPv4 addresses  in  the subnet that are available.
            o cidrBlock  - The IPv4 CIDR block of the subnet. No wildcards
            o defaultForAz - Indicates whether this is the  default  subnet  for the Availability Zone. You can also
                use default-for-az as the filter name.
            o state - The state of the subnet (pending | available ).
            o subnet-id - The ID of the subnet.
            o tag :key =*value* - The key/value combination of a tag assigned to the resource.
            o tag-key - The key of a tag assigned to the resource.  This  filter
                is  independent  of  the tag-value filter. For example, if you use
                both the filter "tag-key=Purpose" and  the  filter  "tag-value=X",
                you  get  any resources assigned both the tag key Purpose (regard-
                less of what the tag's value is), and the tag value X  (regardless
                of  what  the  tag's  key  is). If you want to list only resources
                where Purpose is X, see the tag :key =*value* filter.
            o tag-value - The value of a tag assigned to the resource. This filter is independent of the tag-key filter
            o vpc-id - The ID of the VPC for the subnet.
        """
        command = ['ec2', 'describe-subnets', '--region', self.region,
                   '--filter',
                   'Name=vpc-id,Values={0}'.format(self.vpc),
                   'Name=cidrBlock,Values={0}'.format(self.cidr),
                   # 'Name=tag:Name,Values={0}'.format(self.name)  # TODO: dynamic tag search bool based on arg
                   ]
        result = bin_aws(command)['Subnets']
        if not result:
            return False
        if len(result) > 1:
            raise TooMany('More than 1 result returned from command {0}'.format(command))
        pprint(result)
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True

    def _create(self):
        """ create-subnet

        --vpc-id <value>
        --cidr-block <value>
        [--availability-zone <value>]
        """
        command = ['ec2', 'create-subnet', '--region', self.region,
                   '--vpc-id', self.vpc,
                   '--cidr-block', self.cidr,
                   ]
        if self.zone:
            command.append('--availability-zone')
            command.append(must.be_string(self.zone))
        # result = bin_aws(command)
        print('Created {0}'.format(command))  # TODO: Log(...)
        command = ['ec2', 'create-tags',
                   '--region', self.region,
                   '--resources', self.id,
                   '--tags', 'Key=Name,Value={0}'.format(self.name)
                   ]
        # bin_aws(command)
        print('Named {0}'.format(command))  # TODO: Log(...)
        return True
