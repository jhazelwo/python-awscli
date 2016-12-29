#!/usr/bin/env python3
""" -*- coding: utf-8 -*- """
from pprint import pprint
from awscli import awscli
import exception
import must

"""

          [--db-name <value>]
          --db-instance-identifier <value>
          [--allocated-storage <value>]
          --db-instance-class <value>
          --engine <value>
          [--master-username <value>]
          [--master-user-password <value>]
          [--db-security-groups <value>]
          [--vpc-security-group-ids <value>]
          [--availability-zone <value>]
          [--db-subnet-group-name <value>]
          [--preferred-maintenance-window <value>]
          [--db-parameter-group-name <value>]
          [--backup-retention-period <value>]
          [--preferred-backup-window <value>]
          [--port <value>]
          [--multi-az | --no-multi-az]
          [--engine-version <value>]
          [--auto-minor-version-upgrade | --no-auto-minor-version-upgrade]
          [--license-model <value>]
          [--iops <value>]
          [--option-group-name <value>]
          [--character-set-name <value>]
          [--publicly-accessible | --no-publicly-accessible]
          [--tags <value>]
          [--db-cluster-identifier <value>]
          [--storage-type <value>]
          [--tde-credential-arn <value>]
          [--tde-credential-password <value>]
          [--storage-encrypted | --no-storage-encrypted]
          [--kms-key-id <value>]
          [--domain <value>]
          [--copy-tags-to-snapshot | --no-copy-tags-to-snapshot]
          [--monitoring-interval <value>]
          [--monitoring-role-arn <value>]
          [--domain-iam-role-name <value>]
          [--promotion-tier <value>]
          [--timezone <value>]

"""


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
        return True
