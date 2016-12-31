""" -*- coding: utf-8 -*- """

from python2awscli import bin_aws


class BaseVPC(object):
    def __init__(self, name, region, cidr, ipv6=False):
        self.id = None
        self.name = name
        self.region = region
        self.cidr = cidr
        self.ipv6 = ipv6  # Only available in us-east-2 (Ohio)
        if not self._get():
            self._create()

    def _get(self):
        """
        Get information about VPC from AWS and update self
        :return: Bool
        """
        command = ['ec2', 'describe-tags', '--region', self.region,
                   '--filter',
                   'Name=resource-type,Values=vpc',
                   'Name=value,Values={0}'.format(self.name)]
        result = bin_aws(command, key='Tags', max=1)
        if not result:
            return False
        self.id = result[0]['ResourceId']
        command = ['ec2', 'describe-vpcs', '--region', self.region,
                   '--vpc-ids', self.id]
        result = bin_aws(command, key='Vpcs', max=1)
        self.cidr = result[0]['CidrBlock']
        self.id = result[0]['VpcId']
        if 'Ipv6CidrBlockAssociationSet' in result[0]:
            self.ipv6 = True
        else:
            self.ipv6 = False
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True

    def _create(self):
        """
        Create a VPC
        IPv6 Error:
        "An error occurred (InvalidParameter) when calling the CreateVpc operation:
            The parameter amazon-provided-ipv6-cidr-block is not recognized"
        means IPv6 is not yet available in the region given.
        https://github.com/aws/aws-cli/issues/2343
        :return:
        """
        command = ['ec2', 'create-vpc',
                   '--region', self.region,
                   '--cidr-block', self.cidr,
                   ]
        if self.ipv6:
            command.append('--amazon-provided-ipv6-cidr-block')
        result = bin_aws(command)
        print('Created {0}'.format(command))  # TODO: Log(...)
        self.id = result['Vpc']['VpcId']
        command = ['ec2', 'create-tags',
                   '--region', self.region,
                   '--resources', self.id,
                   '--tags', 'Key=Name,Value={0}'.format(self.name)
                   ]
        bin_aws(command, decode_output=False)
        print('Named {0}'.format(command))  # TODO: Log(...)
        return True
