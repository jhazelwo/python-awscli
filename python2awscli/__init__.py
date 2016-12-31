""" -*- coding: utf-8 -*- """
import json
from subprocess import Popen, PIPE

from python2awscli.error import AWSDuplicate, AWSNotFound, AWSCLIError, TooMany

VERSION = "0.a"


def bin_aws(arguments, timeout=30, decode_output=True, max=0, key=None):
    """
    Run /usr/local/bin/aws as current user, kill process if running for more than 'timeout' seconds.

    This app is meant to be run in an known Docker container so there is no need to provide a
    way to override the path to the aws binary (at this time)

    :param arguments: List of strings to append to bin/aws
    :param timeout: Int, max TTL of command execution
    :param decode_output: Bool, whether to json-decode STDOUT, default is True because most bin/aws output is json.
    :param max: Int (0=unlimited) raise error if number of valid elements returned from command is greater
    :param key: Str, return d[key] instead of d
    :return:
    """
    standard_out = '{}'
    standard_err = ''
    command_list = ['/usr/local/bin/aws'] + arguments
    try:
        cmd0 = Popen(command_list, stdout=PIPE, stderr=PIPE)
    except:
        print(command_list)
        raise
    try:
        outs, errs = cmd0.communicate(timeout=timeout)
    except TimeoutError:
        cmd0.kill()
        raise
    # TODO: Log(cmd0.args)
    if outs:
        standard_out = outs.decode('utf-8')
    if errs:
        standard_err = errs.decode('utf-8')
    if cmd0.returncode == 0:
        if decode_output:
            try:
                d = json.loads(standard_out)
                if key:
                    d = d[key]
                if max and len(d) > max:
                    raise TooMany('More than {0} results returned for command {1}'.format(max, arguments))
            except json.decoder.JSONDecodeError:
                print('Contact Dev, failed to decode STDOUT "{0}"'.format(standard_out))
                raise
            return d
        else:
            return standard_out
    error = '{0}\n{1}'.format(cmd0.args, standard_err)
    if 'Duplicate) ' in standard_err:
        raise AWSDuplicate(error)
    if 'NotFound) ' in standard_err:
        raise AWSNotFound(error)
    raise AWSCLIError(error)
