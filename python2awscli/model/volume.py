#!/usr/bin/env python3
""" -*- coding: utf-8 -*- """
import time
from pprint import pprint
from awscli import awscli

import exception


class BaseVolume(object):
    def __init__(self, name, region, size, zone, instance=None, device=None, kind='standard'):
        self.id = None
        self.name = name
        self.region = region
        self.size = size  # Size in GB
        self.zone = zone
        self.kind = kind  # standard | io1| gp2| sc1| st1
        self.instance = instance
        self.device = device
        if not self._get():
            self._create()
            self._attach()

    def _attach(self):
        timeout = 30
        while timeout > 0:
            time.sleep(1)
            timeout -= 1
            if timeout < 1:
                raise TimeoutError
            command = ['ec2', 'describe-volumes', '--region', self.region]
            result = awscli(command)['Volumes']
            if not result:
                return False  # TODO: raise ImpossibleState(describe returned nothing)
            for this in result:
                if this['VolumeId'] == self.id:
                    if this['State'] == 'available':
                        if self.instance and self.device:
                            command = ['ec2', 'attach-volume', '--region', self.region,
                                       '--volume-id', self.id,
                                       '--instance-id', self.instance,
                                       '--device', self.device
                                       ]
                            result = awscli(command)
                            pprint(result)
                            print('Attach {0}'.format(command))  # TODO: Log(...)
                            return True
                    else:
                        print('Waiting for {0} to be available'.format(self.id))
        return self.instance

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
            raise exception.TooMany('volume._get() returned more than 1 result. Command={0}'.format(command))
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
