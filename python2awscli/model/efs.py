#!/usr/bin/env python3
""" -*- coding: utf-8 -*- """
import uuid


class BaseEFS(object):
    def __init__(self, name, region, kind, zones):
        self.name = name
        self.token = uuid.uuid5(uuid.NAMESPACE_URL, self.name)
        self.region = region
        self.kind = kind
        self.zones = zones

    def _create(self):
        pass

    def _get(self):
        pass
