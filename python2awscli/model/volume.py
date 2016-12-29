#!/usr/bin/env python3
""" -*- coding: utf-8 -*- """
from time import sleep
from pprint import pprint

from python2awscli import bin_aws as awscli
from python2awscli.error import TooMany, ParseError


class BaseVolume(object):
    def __init__(self, name, region, size, zone, instance=None, device=None, kind='standard'):
        self.id = None
        self.name = name
        self.region = region
        self.size = size  # Size in GB
        self.zone = zone
        self.kind = kind  # standard | io1| gp2 | sc1| st1
        self.instance = instance
        self.device = device
        if not self._get():
            self._create()
            self._attach()

    def _attach(self):
        if not self.instance and not self.device:
            return False
        if not self.instance or not self.device:
            raise ParseError('{0}: device and instance are both required, else omit both'.format(self.name))
        for i in range(30):
            print('Waiting for volume {0} to be available'.format(self.id))
            sleep(1)
            command = ['ec2', 'describe-volumes', '--region', self.region,
                       '--volume-ids', self.id
                       ]
            result = awscli(command)['Volumes']
            if len(result) > 1:
                raise TooMany('volume._attach() returned more than 1 result. Command={0}'.format(command))
            if result[0]['State'] == 'available':
                command = ['ec2', 'attach-volume', '--region', self.region,
                           '--volume-id', self.id,
                           '--instance-id', self.instance,
                           '--device', self.device
                           ]
                awscli(command)
                print('Attached {0}'.format(command))  # TODO: Log(...)
                return True
        raise TimeoutError

    def _get(self):
        command = ['ec2', 'describe-volumes', '--region', self.region,
                   '--filters',
                   'Name=attachment.device,Values={0}'.format(self.device),
                   'Name=attachment.instance-id,Values={0}'.format(self.instance),
                   ]
        result = awscli(command)['Volumes']
        if not result:
            return False
        if len(result) > 1:
            raise TooMany('volume._get() returned more than 1 result. Command={0}'.format(command))
        self.id = result[0]['VolumeId']
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True

    def _create(self):
        command = ['ec2', 'create-volume', '--region', self.region,
                   '--size', self.size,
                   '--volume-type', self.kind,
                   '--availability-zone', self.zone
                   ]
        result = awscli(command)
        self.id = result['VolumeId']
        print('Created {0}'.format(command))  # TODO: Log(...)
        command = ['ec2', 'create-tags',
                   '--region', self.region,
                   '--resources', self.id,
                   '--tags', 'Key=Name,Value={0}'.format(self.name)
                   ]
        awscli(command)  # No output on success
        print('Named {0}'.format(command))  # TODO: Log(...)
        return True
