""" -*- coding: utf-8 -*- """
import os
import fileasobj

from python2awscli import bin_aws
from python2awscli.error import AWSNotFound, AWSDuplicate


class BaseKeyPair(object):
    def __init__(self, directory, name, region):
        self.directory = directory
        self.name = name
        self.region = region
        self.fingerprint = None
        try:
            self._get()
        except AWSNotFound:
            self._create()
            self._get()

    def _create(self):
        path_to_key = os.path.join(self.directory, '{0}.pem'.format(self.name))
        try:
            private_key = fileasobj.FileAsObj(path_to_key)
        except FileNotFoundError:
            private_key = fileasobj.FileAsObj()
            private_key.filename = path_to_key
        if private_key.contents:
            raise AWSDuplicate('Non-empty file {0} already exists.'.format(path_to_key))
        private_key.save()  # Make sure we can write to the file before starting work.
        command = ['ec2', 'create-key-pair', '--region', self.region,
                   '--key-name', self.name,
                   '--query', 'KeyMaterial',
                   '--output', 'text']
        result = bin_aws(command, decode_output=False)
        private_key.add(result)
        private_key.save()
        print('Created {0}'.format(command))  # TODO: Log(...)
        return True

    def _get(self):
        command = ['ec2', 'describe-key-pairs', '--region', self.region,
                   '--key-names', self.name]
        result = bin_aws(command)
        if not result:
            return False
        self.fingerprint = result['KeyPairs'][0]['KeyFingerprint']
        print('Got {0}'.format(command))  # TODO: Log(...)
        return True
