""" -*- coding: utf-8 -*-
Do one thing, and do it well."""
import re

from python2awscli.error import ParseError


def is_ip(address):
    """
    :param address: String, format is (keyword|network/cidr|ip):(port|any)

        Valid input examples:
            10.10.0.0/16
            0.0.0.0/0
            192.168.1.2/32
    """
    # Construct a super-valid IP regex for matching operations.
    ioct = '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9]|0)'
    ipregex = '^{ioct}\.{ioct}\.{ioct}\.{ioct}$'.format(ioct=ioct)

    check = re.compile(ipregex, re.IGNORECASE)
    result = check.search(str(address))
    if result:
        return result
    return False


def make_ipperms(s):
    """
    string can be:
        1.2.3.4/32:80/tcp
        sg-b4b3b4b3/0123456789:80/tcp

    No IPv6 support in this function yet.
    Also cannot handle multiple ip or group rules yet.
    There is only enough input checking to decide if IP or Group. Let bin/aws handle real validation.
    :param s: String
    :return: Dict
    """
    s = s.lower()
    try:
        ipmask, portproto = s.split(':')  # I fail on IPv6! FIXME
        ip, mask = ipmask.split('/')
        port, protocol = portproto.split('/')
    except ValueError:
        raise ParseError(
            'Malformed rule string {0}. expected "ip/mask:port/protocol" or "group/owner:port/protocol"'.format(s))
    ipranges = []
    ip6ranges = []
    useridgrouppairs = []
    if is_ip(ip):
        ipranges = [{'CidrIp': '{0}/{1}'.format(ip, mask)}]
    elif ip[:3] == 'sg-':
        useridgrouppairs = [{'GroupId': ip, 'UserId': mask}]
    else:
        ip6ranges = [{"CidrIpv6": '{0}/{1}'.format(ip, mask)}]
    d = {
        'FromPort': int(port),
        'IpProtocol': protocol,
        'IpRanges': ipranges,
        'Ipv6Ranges': ip6ranges,
        'PrefixListIds': [],
        'ToPort': int(port),
        'UserIdGroupPairs': useridgrouppairs
    }
    return d


def merge_elements(requested, existing, add_function, rm_function, add_first=False):
    if add_first:
        for this in requested:
            if this not in existing:
                add_function(this)   # Requested but does not exist, add
    for this in existing:
        if this not in requested:
            rm_function(this)  # Exists but not requested, remove
    for this in requested:
        if this not in existing:
            add_function(this)  # Requested but does not exist, add
    return True


def make_listener(s):
    """
    Format a listener for the CLI from a simplified string.

    Convert:
        '80/http>8100/http'
        '443/https>8100/http+us-west-2:03216549873:certificate/b4b3b4b3-b4b3-b4b3-b4b3b4b3'
    To:
        {
            'InstancePort': 80,
            'InstanceProtocol': 'HTTP',
            'LoadBalancerPort': 80,
            'Protocol': 'HTTP'
            },
        {
            'InstancePort': 80,
            'InstanceProtocol': 'HTTP',
            'LoadBalancerPort': 443,
            'Protocol': 'HTTPS',
            'SSLCertificateId': 'arn:aws:acm:us-west-2:03216549873:certificate/b4b3b4b3-b4b3-b4b3-b4b3b4b3'
        },
    :param s: String
    :return: Dict
    """
    s = s.lower()
    cert = False
    try:
        if '+' in s:
            s, cert = s.split('+')
        external, internal = s.split('>')
        external_port, external_protocol = external.split('/')
        internal_port, internal_protocol = internal.split('/')
    except ValueError:
        raise ParseError("""
        Malformed argument for make_listener()
        Need format like '80/http>80/http' or '443/https>80/http+us-west-2:0123456789:certificate/uuid-string'
        but got '{0}'""".format(s)
        )
    d = {
        'InstancePort': int(internal_port),
        'InstanceProtocol': internal_protocol.upper(),
        'LoadBalancerPort': int(external_port),
        'Protocol': external_protocol.upper(),
    }
    if cert:
        d['SSLCertificateId'] = 'arn:aws:acm:{0}'.format(cert)
    return d
