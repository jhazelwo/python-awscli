""" -*- coding: utf-8 -*- """
import uuid
from pprint import pprint

from python2awscli import bin_aws


class BaseEFS(object):
    def __init__(self, name, region, kind, zones, subnet, mount=None):
        self.name = name
        self.token = uuid.uuid5(uuid.NAMESPACE_URL, self.name)
        self.region = region
        self.kind = kind
        self.zones = zones
        self.subnet = subnet
        self.mount = mount
        if not mount:
            self.mount = name

    def _create(self):
        command = ['efs', 'create-file-system', '--region', self.region,
                   ]
        result = bin_aws(command)
        pprint(result)
        command = ['efs', 'create-mount-target', '--region', self.region,
                   ]
        result = bin_aws(command)
        pprint(result)

    def _get(self):
        command = ['efs', 'describe-file-systems', '--region', self.region,
                   ]
        result = bin_aws(command)['FileSystems']
        pprint(result)

