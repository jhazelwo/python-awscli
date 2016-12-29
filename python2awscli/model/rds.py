""" -*- coding: utf-8 -*- """
from pprint import pprint

import must
from awscli import awscli


class BaseRDS(object):
    def __init__(self, name, region, engine, size, username, password, gb, zone, groups, public=True):
        self.id = None  # DbiResourceId
        self.name = name  # DBName
        self.region = region
        self.engine = engine  # Engine
        self.size = size  # DBInstanceClass
        self.dns = None  # {'Endpoint: {'Address:
        self.username = username  # MasterUsername
        self.password = password  # MasterUserPassword
        self.gb = gb  # AllocatedStorage
        self.zone = zone  # AvailabilityZone
        self.groups = groups  # DBSecurityGroups
        #
        self.public = public  # PubliclyAccessible
        if not self._get():
            self._create()

    def _get(self):
        command = ['rds', 'describe-db-instances', '--region', self.region]
        result = awscli(command)['DBInstances']
        found = must.find.dict_in_list(key='DBName', needle=self.name, haystack=result)
        if not found:
            return False
        self.id = found['DbiResourceId']
        self.engine = found['Engine']
        self.groups = found['DBSecurityGroups']
        self.zone = found['AvailabilityZone']
        self.gb = found['AllocatedStorage']
        self.username = found['MasterUsername']
        if 'Endpoint' in found:
            self.dns = found['Endpoint']['Address']
        self.public = found['PubliclyAccessible']
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True

    def _create(self):
        command = ['rds', 'create-db-instance', '--region', self.region,
                   '--db-instance-identifier', self.name,
                   '--db-name', self.name,
                   '--db-instance-class', self.size,
                   '--engine', self.engine,
                   '--master-username', self.username,
                   '--master-user-password', self.password,
                   '--availability-zone', self.zone,
                   '--allocated-storage', must.be_string(self.gb),
                   '--vpc-security-group-ids'
                   ]
        command.extend(self.groups)
        result = awscli(command)
        pprint(result)
        print('Created {0}'.format(command))  # TODO: Log(...)
        return True
