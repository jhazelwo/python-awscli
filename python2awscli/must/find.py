""" -*- coding: utf-8 -*- """


def dict_in_list(key, needle, haystack):
    """
    Look through haystack for a dict where value of key is needle
    :param key:
    :param needle:
    :param haystack: list
    :return:
    """
    for this in haystack:
        if this[key] == needle:
            return this
    return False
