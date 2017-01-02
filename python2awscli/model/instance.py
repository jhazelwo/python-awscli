""" -*- coding: utf-8 -*- """
from pprint import pprint

from python2awscli import bin_aws as awscli
from python2awscli.error import TooMany, AWSNotFound
from python2awscli import must



class BaseInstance(object):
    def __init__(self, name, region, vpc, image, key, count, size, groups, zone=None, public=True, script=None):
        self.name = name
        self.region = region
        self.vpc = vpc
        self.image = image
        self.key = key
        self.count = must.be_int(count)
        self.deficit = 0  # Should always be negative inventory (requested - running)
        self.size = size  # --instance-type
        self.groups = must.be_list(groups)  # --security-group-ids
        self.id = set()
        self.subnets = set()
        self.public_ips = set()
        self.private_ips = set()
        self.public = public
        self.script = script
        self.zones = set()
        self.zone = zone  # AZ to use during _create()
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
        if self.zone:
            placement = {
                "AvailabilityZone": self.zone,
                "GroupName": "",
                "Tenancy": "default",
            }
            command.append('--placement')
            command.append(str(placement).replace("'", '"'))
        if self.script:
            command.append('--user-data')
            command.append('file://{0}'.format(self.script))
        instances = awscli(command, key='Instances')
        print('Created {0}'.format(command))  # TODO: Log(...)
        for this in instances:
            self.id.add(this['InstanceId'])
            command = ['ec2', 'create-tags',
                       '--region', self.region,
                       '--resources', this['InstanceId'],
                       '--tags', 'Key=Name,Value={0}'.format(self.name)
                       ]
            awscli(command, decode_output=False)
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
        # This does not filter the way we expected it to.
        # It looks like if any of the instance Ids are not all placed in self.zone then NotFound is raised for all.
        # if self.zone:
        #     command.append('--filter',)
        #     command.append('Name=availability-zone,Values={0}'.format(self.zone))
        reservations = awscli(command, key='Reservations')
        all_instances = []  # Will become list() of ALL instances (even terminated) as dict()s
        for this in reservations:  # Extract Instances from each Reservation and merge them into a list()
            all_instances.extend(this['Instances'])
        for this in all_instances:
            if this['State']['Code'] in [0, 16]:  # "Pending, Running"
                if self.zone is None or self.zone == this['Placement']['AvailabilityZone']:
                    self.zones.add(this['Placement']['AvailabilityZone'])
                    self.id.add(this['InstanceId'])
                    if 'PrivateIpAddress' in this:
                        self.private_ips.add(this['PrivateIpAddress'])
                    if 'PublicIpAddress' in this:
                        self.public_ips.add(this['PublicIpAddress'])
                    if 'SubnetId' in this:
                        self.subnets.add(this['SubnetId'])
        running_count = len(self.id)
        need_running = self.count
        if running_count != need_running:
            self.deficit = need_running - running_count
            return False
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True
