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


def quiet_hook(kind, message, traceback):
    if kind in [AWSCLIError, ParseError, TooMany, AWSNotFound, AWSDuplicate]:
        print('{0}: {1}'.format(kind.__name__, message))
    else:
        sys.__excepthook__(kind, message, traceback)

sys.excepthook = quiet_hook
