""" -*- coding: utf-8 -*- """

import sys


class QuietError(Exception):
    # All who inherit me shall not traceback, but be spoken of cleanly
    pass


class AWSCLIError(QuietError):
    # Generic error when the bin/aws cli exits with a non-zero status
    pass


class ParseError(QuietError):
    # Failed to parse data
    pass


class MissingArgument(QuietError):
    # A conditionally-required argument is not present
    pass


class ArgumentError(QuietError):
    # Some other problem with arguments
    pass


class TooMany(QuietError):
    # Too many results returned or values to unpack
    pass


class AWSNotFound(QuietError):
    # Resource does not exist in AWS
    pass


class AWSDuplicate(QuietError):
    # Resource already exists in AWS
    pass


def quiet_hook(kind, message, traceback):
    if QuietError in kind.__bases__:
        print('{0}: {1}'.format(kind.__name__, message))
    else:
        sys.__excepthook__(kind, message, traceback)

sys.excepthook = quiet_hook
