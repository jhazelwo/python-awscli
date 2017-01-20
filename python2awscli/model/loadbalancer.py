""" -*- coding: utf-8 -*- """

from python2awscli import bin_aws
from python2awscli.task import merge_elements
from python2awscli.error import AWSNotFound
from python2awscli import must


class BaseLoadBalancer(object):
    def __init__(self, name, region, listeners, instances=None, subnets=None, zones=None, groups=None, scheme=None):
        """
        :param name: String, name of LB
        :param region: String, AWS region
        :param listeners: list() of Listeners, funct make_listener() can help with formatting
        :param subnets: list() of Subnets
        :param zones: list() of Availability Zones
        :param groups: list() of Security Group IDs
        :param scheme: String or None. Can be 'internal', otherwise LB is Internet-facing
        """
        self.dns = None
        self.name = name
        self.region = region
        self.listeners = []
        self.subnets = subnets
        self.zones = []
        self.groups = []
        self.scheme = None
        self.vpc = None
        self.instances = []
        instances = must.be_list(instances)
        listeners = must.be_list(listeners)
        groups = must.be_list(groups)
        zones = must.be_list(zones)
        try:
            self._get()
        except AWSNotFound:
            self._create(zones, groups, scheme, listeners)
        if self.groups != groups:
            self._groups(groups)
        merge_elements(listeners, self.listeners, self._add_listener, self._rm_listener)
        merge_elements(zones, self.zones, self._add_zone, self._rm_zone, add_first=True)
        merge_elements(instances, self.instances, self._add_instance, self._rm_instance)

    def _get(self):
        command = ['elb', 'describe-load-balancers', '--region', self.region,
                   '--load-balancer-names', self.name]
        result = bin_aws(command)
        base = result['LoadBalancerDescriptions'][0]
        self.dns = base['DNSName']
        self.groups = base['SecurityGroups']
        self.scheme = base['Scheme']
        self.zones = base['AvailabilityZones']
        self.subnets = base['Subnets']
        self.vpc = base['VPCId']
        for this in base['Instances']:
            if this['InstanceId'] not in self.instances:
                self.instances.append(this['InstanceId'])
        for listen in base['ListenerDescriptions']:
            if listen['Listener'] not in self.listeners:
                self.listeners.append(listen['Listener'])
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True

    def _add_zone(self, zone):
        command = ['elb', 'enable-availability-zones-for-load-balancer', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--availability-zones', zone
                   ]
        bin_aws(command)
        self.zones.append(zone)
        print('Enabled {0}'.format(command))  # TODO: Log(...)
        return True

    def _rm_zone(self, zone):
        command = ['elb', 'disable-availability-zones-for-load-balancer', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--availability-zones', zone
                   ]
        bin_aws(command)
        self.zones.remove(zone)
        print('Disabled {0}'.format(command))  # TODO: Log(...)
        return True

    def _add_listener(self, listener):
        command = ['elb', 'create-load-balancer-listeners', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--listeners', str(listener).replace("'", '"')
                   ]
        bin_aws(command)
        self.listeners.append(listener)
        print('Added {0}'.format(command))  # TODO: Log(...)
        return True

    def _rm_listener(self, listener):
        command = ['elb', 'delete-load-balancer-listeners', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--load-balancer-ports', str(listener['LoadBalancerPort'])
                   ]
        bin_aws(command)
        self.listeners.remove(listener)
        print('Removed {0}'.format(command))  # TODO: Log(...)
        return True

    def _add_instance(self, instances):
        instances = must.be_list(instances)
        command = ['elb', 'register-instances-with-load-balancer', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--instances']
        command.extend(instances)
        bin_aws(command)
        for this in instances:
            if this not in self.instances:
                self.instances.append(this)
        print('Registered {0}'.format(command))  # TODO: Log(...)
        return True

    def _rm_instance(self, instances):
        instances = must.be_list(instances)
        command = ['elb', 'deregister-instances-from-load-balancer', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--instances']
        command.extend(instances)
        bin_aws(command)
        for this in instances:
            if this in self.instances:
                self.instances.remove(this)
        print('Deregistered {0}'.format(command))  # TODO: Log(...)
        return True

    def _create(self, zones, groups, scheme, listeners):
        command = ['elb', 'create-load-balancer', '--region', self.region, '--load-balancer-name', self.name]
        if scheme is not None:
            command.append('--scheme')
            command.append(scheme)
        if groups is not None:
            command.append('--security-groups')
            command.extend(groups)
        if zones is not None:
            command.append('--availability-zones')
            command.extend(zones)
        command.append('--listeners')
        for listen in listeners:
            command.append(str(listen).replace("'", '"'))  # Convert Dictionaries to Strings for JSON
        result = bin_aws(command)
        self.dns = result['DNSName']
        self.zones = zones
        self.groups = groups
        self.listeners = listeners
        print('Created {0}'.format(command))  # TODO: Log(...)
        return True

    def _attach(self, instances):
        if not instances:
            return False
        command = ['elb','register-instances-with-load-balancer', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--instances']
        command.extend(instances)
        bin_aws(command, decode_output=False)
        print('Attached {0}'.format(command))  # TODO: Log(...)

    def _detach(self, instances):
        if not instances:
            return False
        command = ['elb', 'deregister-instances-from-load-balancer', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--instances']
        command.extend(instances)
        bin_aws(command, decode_output=False)
        print('Detached {0}'.format(command))  # TODO: Log(...)

    def _groups(self, groups):
        command = ['elb', 'apply-security-groups-to-load-balancer', '--region', self.region,
                   '--load-balancer-name', self.name,
                   '--security-groups'
                   ]
        command.extend(groups)
        bin_aws(command, decode_output=False)
        print('Applied {0}'.format(command))  # TODO: Log(...)
