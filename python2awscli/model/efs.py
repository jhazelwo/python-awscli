""" -*- coding: utf-8 -*- """
import uuid
from pprint import pprint

from python2awscli import bin_aws
from python2awscli import must


class BaseEFS(object):
    def __init__(self, name, region, kind, subnets, groups):
        self.id = None
        self.targets = None
        self.name = name
        # self.token = uuid.uuid5(uuid.NAMESPACE_URL, self.name)
        self.token = 'console-b6a9d34e-7a9c-4934-b773-34b2a60221a7'
        self.region = region
        self.kind = kind  # generalPurpose | maxIO
        self.subnets = must.be_list(subnets)
        self.groups = must.be_list(groups)
        if not self._get():
            print('create')
        pprint(vars(self))

    def _create(self):
        command = ['efs', 'create-file-system', '--region', self.region,
                   '--creation-token', self.token,
                   '--performance-mode', self.kind
                   ]
        result = bin_aws(command)
        pprint(result)
        print('Created {0}'.format(command))  # TODO: Log(...)
        """
        create-mount-target
        --file-system-id <value>
        --subnet-id <value>
        [--ip-address <value>]
        [--security-groups <value>]
        """
        for this in self.subnets:
            command = ['efs', 'create-mount-target', '--region', self.region,
                       '--file-system-id', self.token,
                       '--subnet-id', this,
                       '--security-groups', self.groups,
                       ]
            result = bin_aws(command)
            pprint(result)
            print('Made {0}'.format(command))  # TODO: Log(...)
        return True

    def _get(self):
        command = ['efs', 'describe-file-systems', '--region', self.region,
                   '--creation-token', self.token
                   ]
        result = bin_aws(command)['FileSystems']
        if not result:
            return False
        self.id = result[0]['FileSystemId']
        command = ['efs', 'describe-mount-targets', '--region', self.region,
                   '--file-system-id', self.id
                   ]
        result = bin_aws(command)['MountTargets']
        if not result:
            raise TypeError('TODO')
        pprint(result)
        self.targets = result
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True
