""" -*- coding: utf-8 -*- """

from . import instance, loadbalancer, vpc, securitygroup, keypair, rds, volume, efs


class Instance(instance.BaseInstance):
    pass


class LoadBalancer(loadbalancer.BaseLoadBalancer):
    pass


class VPC(vpc.BaseVPC):
    pass


class SecurityGroup(securitygroup.BaseSecurityGroup):
    pass


class KeyPair(keypair.BaseKeyPair):
    pass


class RDS(rds.BaseRDS):
    pass


class Volume(volume.BaseVolume):
    pass


class EFS(efs.BaseEFS):
    pass
