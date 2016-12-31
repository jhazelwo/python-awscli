""" -*- coding: utf-8 -*- """
import uuid
from time import sleep

from python2awscli import bin_aws
from python2awscli import must


class BaseEFS(object):
    def __init__(self, name, region, kind, subnets, groups):
        self.id = None
        self.targets = None
        self.name = name
        self.token = str(uuid.uuid5(uuid.NAMESPACE_URL, self.name))
        self.region = region
        self.kind = kind  # generalPurpose | maxIO
        self.subnets = must.be_list(subnets)
        self.groups = must.be_list(groups)
        if not self._get():
            self._create()
        self._mounts()

    def _mounts(self):
        for i in range(30):
            command = ['efs', 'describe-file-systems', '--region', self.region,
                       '--creation-token', self.token]
            file_systems = bin_aws(command, key='FileSystems', max=1)
            if file_systems[0]['LifeCycleState'] == 'available':
                command = ['efs', 'describe-mount-targets', '--region', self.region,
                           '--file-system-id', self.id]
                mount_targets = bin_aws(command, key='MountTargets')
                for this in self.subnets:
                    if not must.find.dict_in_list(key='SubnetId', needle=this, haystack=mount_targets):
                        command = ['efs', 'create-mount-target', '--region', self.region,
                                   '--file-system-id', self.id,
                                   '--subnet-id', this,
                                   '--security-groups']
                        command.extend(self.groups)
                        bin_aws(command, decode_output=False)
                        print('Made {0}'.format(command))  # TODO: Log(...)
                return True
            else:
                print('Waiting for EFS {0} to be available'.format(self.id))
                sleep(1)
        raise TimeoutError

    def _create(self):
        command = ['efs', 'create-file-system', '--region', self.region,
                   '--creation-token', self.token,
                   '--performance-mode', self.kind
                   ]
        result = bin_aws(command)
        self.id = result['FileSystemId']
        print('Created {0}'.format(command))  # TODO: Log(...)
        command = ['efs', 'create-tags',
                   '--region', self.region,
                   '--file-system-id', self.id,
                   '--tags', 'Key=Name,Value={0}'.format(self.name)
                   ]
        bin_aws(command, decode_output=False)
        print('Named {0}'.format(command))  # TODO: Log(...)
        return True

    def _get(self):
        command = ['efs', 'describe-file-systems', '--region', self.region,
                   '--creation-token', self.token
                   ]
        file_systems = bin_aws(command, key='FileSystems', max=1)
        if not file_systems:
            return False
        self.id = file_systems[0]['FileSystemId']
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True
