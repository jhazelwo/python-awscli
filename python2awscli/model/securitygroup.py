""" -*- coding: utf-8 -*- """

from python2awscli import bin_aws
from python2awscli.error import AWSNotFound, ParseError, AWSDuplicate
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
        self.changed = False
        try:
            self._get()
        except AWSNotFound:
            self._create()
        self._merge_rules(must.be_list(inbound), self.IpPermissions)
        self._merge_rules(must.be_list(outbound), self.IpPermissionsEgress, egress=True)
        if self.changed:
            self._get()

    def _break_out(self, existing):
        """
        Undo AWS's rule flattening so we can do simple 'if rule in existing' logic later.
        :param existing: List of SG rules as dicts.
        :return: List of SG rules as dicts.
        """
        spool = list()
        for rule in existing:
            for ip in rule['IpRanges']:
                copy_of_rule = rule.copy()
                copy_of_rule['IpRanges'] = [ip]
                copy_of_rule['UserIdGroupPairs'] = []
                spool.append(copy_of_rule)
            for group in rule['UserIdGroupPairs']:
                copy_of_rule = rule.copy()
                copy_of_rule['IpRanges'] = []
                copy_of_rule['UserIdGroupPairs'] = [group]
                spool.append(copy_of_rule)
        return spool

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
        if egress:
            direction = 'authorize-security-group-egress'
        command = ['ec2', direction,
                   '--region', self.region,
                   '--group-id', self.id,
                   '--ip-permissions', str(ip_permissions).replace("'", '"')
                   ]
        bin_aws(command)
        print('Authorized: {0}'.format(ip_permissions))  # TODO: Log(...)
        self.changed = True
        return True

    def _rm_rule(self, ip_permissions, egress):
        """
        :param ip_permissions: Dict of IP Permissions
        :param egress: Bool
        :return: Bool
        """
        direction = 'revoke-security-group-ingress'
        if egress:
            direction = 'revoke-security-group-egress'
        command = ['ec2', direction,
                   '--region', self.region,
                   '--group-id', self.id,
                   '--ip-permissions', str(ip_permissions).replace("'", '"')
                   ]
        bin_aws(command)
        print('Revoked: {0}'.format(ip_permissions))  # TODO: Log(...)
        self.changed = True
        return True

    def _create(self):
        """
        Create a Security Group
        :return:
        """
        # AWS grants all new SGs this default outbound rule "This is pro-human & anti-machine behavior."
        default_egress = {
            'Ipv6Ranges': [],
            'PrefixListIds': [],
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
            'UserIdGroupPairs': [], 'IpProtocol': '-1'
        }
        command = [
                'ec2', 'create-security-group',
                '--region', self.region,
                '--group-name',  self.name,
                '--description', self.description,
                '--vpc-id', self.vpc
                ]
        try:
            self.id = bin_aws(command, key='GroupId')
        except AWSDuplicate:
            return False  # OK if it already exists.
        print('Created {0}'.format(command))  # TODO: Log(...)
        self.IpPermissions = []
        self.IpPermissionsEgress = [default_egress]
        self.changed = True
        return True

    def _get(self):
        """
        Get information about Security Group from AWS and update self
        :return: Bool
        """
        command = ['ec2', 'describe-security-groups', '--region', self.region, '--group-names', self.name]
        result = bin_aws(command, key='SecurityGroups', max=1)  # will raise NotFound if empty
        me = result[0]
        self.id = me['GroupId']
        self.owner = me['OwnerId']
        self.IpPermissions = self._break_out(me['IpPermissions'])
        self.IpPermissionsEgress = self._break_out(me['IpPermissionsEgress'])
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True

    def _delete(self):
        """
        Delete myself by my own id.
        As of 20170114 no other methods call me. You must do `foo._delete()`
        :return:
        """
        command = ['ec2', 'delete-security-group', '--region', self.region,
                   # '--dry-run',
                   '--group-id', self.id
                   ]
        bin_aws(command, decode_output=False)
        print('Deleted {0}'.format(command))  # TODO: Log(...)
        return True
