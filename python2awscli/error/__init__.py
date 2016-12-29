#!/usr/bin/env python3
""" -*- coding: utf-8 -*- """

import sys


class AWSCLIError(Exception):
    # Generic error when the bin/aws cli exits with a non-zero status.
    pass


class ParseError(Exception):
    # Failed to parse data
    pass


class TooMany(Exception):
    # Too many results returned or values to unpack
    pass


class AWSNotFound(Exception):
    # Resource does not exist in AWS
    pass


class AWSDuplicate(Exception):
    # Resource already exists in AWS
    pass


def quiet_hook(type, value, traceback):
    if type in [AWSCLIError, ParseError, TooMany, AWSNotFound, AWSDuplicate]:
        print('{0}: {1}'.format(type.__name__, value))
    else:
        sys.__excepthook__(type, value, traceback)

sys.excepthook = quiet_hook
