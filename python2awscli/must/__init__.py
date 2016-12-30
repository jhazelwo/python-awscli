""" -*- coding: utf-8 -*-

This code is meant to make life a bit easier for humans.

It is most often used in arguments, for example
    human can pass a string or list of strings to a constructor and it's up to the object's method
    to call must.be_list(arg) change it to a list when needed, and to simply return same if it's already correct

"""
from . import find


def be_string(this):
    # Best effort to turn 'this' into a str.
    if isinstance(this, str):
        return this
    if isinstance(this, int):
        return str(this)
    if isinstance(this, list) or isinstance(this, tuple):
        if len(this) == 1:
            return this[0]
        s = ''
        for e in this:
            s += str(e)
        return s
    raise TypeError('Cannot convert {0}:{1} to str'.format(type(this), this))


def be_list(this):
    # Best effort to turn 'this' into a list
    if this is None:
        return []
    if isinstance(this, list):
        return this
    if isinstance(this, tuple):
        return list(this)
    if isinstance(this, str) or isinstance(this, int) or isinstance(this, dict):
        return [this]
    raise TypeError('Cannot convert {0}:{1} to list'.format(type(this), this))


def be_dict(this):
    # Best effort to turn 'this' in a dict
    if isinstance(this, dict):
        return this
    if isinstance(this, str):
        return {0: this}
    if isinstance(this, list) or isinstance(this, tuple):
        d = {}
        for i in range(len(this)):
            d[i] = this[i]
        return d
    raise TypeError('Cannot convert {0}:{1} to dict'.format(type(this), this))


def be_int(this):
    # Best effort to turn 'this' in an int
    if isinstance(this, int):
        return this
    if isinstance(this, str):
        return int(this)
    raise TypeError('Cannot convert {0}:{1} to int'.format(type(this), this))
