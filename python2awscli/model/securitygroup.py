""" -*- coding: utf-8 -*- """
from pprint import pprint

from python2awscli import bin_aws as awscli
from python2awscli.error import AWSNotFound, ParseError, AWSDuplicate, TooMany
from python2awscli import must


class BaseSecurityGroup(object):
    def __init__(self, name, region, vpc, description, inbound=None, outbound=None):
        """
        :param name: String, name of SG
        :param region: String, AWS region
        :param vpc: String, IP of the VPC this SG belongs to
        :param description: String
        :param inbound: List of dicts, IP Permissions that should exist
        :param outbound: List of dicts, IP Permissions that should exist
        """
        self.id = None
        self.name = name
        self.region = region
        self.vpc = vpc
        self.description = description
        self.IpPermissions = []
        self.IpPermissionsEgress = []
        self.owner = None
        try:
            self._get()
        except AWSNotFound:
            self._create()
            self._get()
        inbound = must.be_list(inbound)
        outbound = must.be_list(outbound)
        self._merge_rules(inbound, self.IpPermissions)
        self._merge_rules(outbound, self.IpPermissionsEgress, egress=True)
        # self._get()  # RFC: disabled to help speed, merge_rules updates self.IpPermissions[Egress]

    def _merge_rules(self, requested, active, egress=False):
        """
        :param requested: List of dicts, IP Permissions that should exist
        :param active: List of dicts, IP Permissions that already exist
        :param egress: Bool, addressing outbound rules or not?
        :return: Bool
        """
        if not isinstance(requested, list):
            raise ParseError(
                'SecurityGroup {0}, need a list of dicts, instead got "{1}"'.format(self.name, requested))
        for rule in requested:
            if rule not in active:
                self._add_rule(rule, egress)
        for active_rule in active:
            if active_rule not in requested:
                self._rm_rule(active_rule, egress)
        return True

    def _add_rule(self, ip_permissions, egress):
        """
        :param ip_permissions: Dict of IP Permissions
        :param egress: Bool
        :return: Bool
        """
        direction = 'authorize-security-group-ingress'
        subject = self.IpPermissions
        if egress:
            subject = self.IpPermissionsEgress
            direction = 'authorize-security-group-egress'
        command = ['ec2', direction,
                   '--region', self.region,
                   '--group-id', self.id,
                   '--ip-permissions', str(ip_permissions).replace("'", '"')
                   ]
        awscli(command)
        subject.append(ip_permissions)  # RFC: This is here for speed, should we use another _get() ?
        print('Authorized: {0}'.format(ip_permissions))  # TODO: Log(...)
        return True

    def _rm_rule(self, ip_permissions, egress):
        """
        :param ip_permissions: Dict of IP Permissions
        :param egress: Bool
        :return: Bool
        """
        direction = 'revoke-security-group-ingress'
        subject = self.IpPermissions
        if egress:
            subject = self.IpPermissionsEgress
            direction = 'revoke-security-group-egress'
        command = ['ec2', direction,
                   '--region', self.region,
                   '--group-id', self.id,
                   '--ip-permissions', str(ip_permissions).replace("'", '"')
                   ]
        awscli(command)
        subject.remove(ip_permissions)  # RFC: This is here for speed, should we use another _get() ?
        print('Revoked: {0}'.format(ip_permissions))  # TODO: Log(...)
        return True

    def _create(self):
        """
        Create a Security Group
        :return:
        """
        command = [
                'ec2', 'create-security-group',
                '--region', self.region,
                '--group-name',  self.name,
                '--description', self.description,
                '--vpc-id', self.vpc
                ]
        try:
            awscli(command)
        except AWSDuplicate:
            return False  # OK if it already exists.
        print('Created {0}'.format(command))  # TODO: Log(...)
        return True

    def _get(self):
        """
        Get information about Security Group from AWS and update self
        :return: Bool
        """
        command = ['ec2', 'describe-security-groups', '--region', self.region, '--group-names', self.name]
        result = awscli(command)
        size = len(result['SecurityGroups'])
        if size != 1:
            raise TooMany('Command {0} expected 1 result, got {1}'.format(command, size))
        security_groups = result['SecurityGroups'][0]
        self.id = security_groups['GroupId']
        self.owner = security_groups['OwnerId']
        self.IpPermissions = security_groups['IpPermissions']
        self.IpPermissionsEgress = security_groups['IpPermissionsEgress']
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True
