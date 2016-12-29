""" -*- coding: utf-8 -*- """
from python2awscli import bin_aws as awscli
from python2awscli.error import TooMany
from python2awscli import must


class BaseInstance(object):
    def __init__(self, name, region, vpc, image, key, count, size, groups, public=True, script=None):
        self.name = name
        self.region = region
        self.vpc = vpc
        self.image = image
        self.key = key
        self.count = must.be_int(count)
        self.deficit = 0  # Should always be negative inventory (requested - running)
        self.size = size  # --instance-type
        self.groups = must.be_list(groups)  # --security-group-ids
        self.id = []
        self.subnets = []
        self.public_ips = []
        self.private_ips = []
        self.public = public
        self.script = script
        self.zone = None  # AV Zone
        if not self._get():
            self._create()
            self._get()

    def _create(self):
        if self.deficit < 1:
            # This should never usually happen but is possible if the User changes the count to a lower
            # number after the original instance(s) were created.
            raise TooMany('Cannot create {0} instances of {1}'.format(self.deficit, self.name))
        command = ['ec2', 'run-instances', '--region', self.region,
                   '--instance-type', self.size,
                   '--count', str(self.deficit),
                   '--key-name', self.key,
                   '--image-id', self.image,
                   '--security-group-ids']
        command.extend(self.groups)
        if not self.public:
            command.append('--no-associate-public-ip-address')
        if self.script:
            command.append('--user-data')
            command.append('file://{0}'.format(self.script))
        result = awscli(command)
        print('Created {0}'.format(command))  # TODO: Log(...)
        instances = result['Instances']
        for this in instances:
            this_id = this['InstanceId']
            if this_id not in self.id:
                self.id.append(this_id)
            command = ['ec2', 'create-tags',
                       '--region', self.region,
                       '--resources', this_id,
                       '--tags', 'Key=Name,Value={0}'.format(self.name)
                       ]
            awscli(command)
            print('Named {0}'.format(command))  # TODO: Log(...)
        self.deficit = 0
        return True

    def _get(self):
        command = ['ec2', 'describe-tags', '--region', self.region,
                   '--filter',
                   'Name=resource-type,Values=instance',
                   'Name=value,Values={0}'.format(self.name)
                   ]
        result = awscli(command)['Tags']
        if not result:
            self.deficit = self.count  # Result is []. Deficit is 100%.
            return False
        command = ['ec2', 'describe-instances', '--region', self.region,
                   '--instance-ids']
        for this in result:
            command.append(this['ResourceId'])
        result = awscli(command)['Reservations']
        all_instances = []  # Will become list() of ALL instances (even terminated) as dict()s
        for this in result:  # Extract Instances from each Reservation and merge them into a list()
            all_instances.extend(this['Instances'])
        for this in all_instances:
            if this['State']['Code'] in [0, 16]:  # "Pending, Running"
                self.zone = this['Placement']['AvailabilityZone']
                if this['InstanceId'] not in self.id:
                    self.id.append(this['InstanceId'])
                if 'PrivateIpAddress' in this and this['PrivateIpAddress'] not in self.private_ips:
                    self.private_ips.append(this['PrivateIpAddress'])
                if 'PublicIpAddress' in this and this['PublicIpAddress'] not in self.public_ips:
                    self.public_ips.append(this['PublicIpAddress'])
                if 'SubnetId' in this and this['SubnetId'] not in self.subnets:
                    self.subnets.append(this['SubnetId'])
        running_count = len(self.id)
        need_running = self.count
        if running_count != need_running:
            self.deficit = need_running - running_count
            return False
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True
