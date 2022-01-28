# -*- coding: utf-8 -*-
"""
    time_helper.py
    ~~~~~~~~~~~~~~

    Containing functions to convert time of different format.

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 20:44
    @python version: 3.8
"""

import time
from calendar import timegm
from datetime import datetime
from tornado import gen


def utc2local(utc_dt):
    """Convert utc datetime to local datetime"""
    return datetime.fromtimestamp(timegm(utc_dt.timetuple()))


def datetime2timestamp(dt):
    return int(timegm(dt.timetuple()) * 1000 + dt.microsecond / 1e3)


def timestamp2datetime(stamp, to_local=False):
    dt = datetime.utcfromtimestamp(stamp / 1e3)
    if to_local:
        return utc2local(dt)
    return dt


def datetime2string(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def local2utc(dt):
    """Convert local time string to utc datetime"""
    return datetime.utcfromtimestamp(time.mktime(dt.timetuple()))


def convert_arbitrary_date_format(date_str):
    formats = [
        '%Y/%m',
        '%Y/%m/%d',
        '%Y-%m',
        '%Y-%m-%d',
        '%Y.%m',
        '%Y.%m.%d',
        '%m-%Y',
        '%b-%Y',
        '%d-%m-%Y',
        '%d-%b-%Y',
    ]

    date = None
    for fmt in formats:
        try:
            date = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if date is None:
        raise (ValueError, 'Invalid datetime string')
    return date


def set_interval(interval):
    """decorator to limit function call in time"""

    def dec(func):
        _ = {'last_time': 0}

        @gen.coroutine
        def _func(*args, **kwargs):
            force = kwargs.pop('force', False)
            if time.time() - _['last_time'] > interval or force:
                yield gen.maybe_future(func(*args, **kwargs))
                _['last_time'] = time.time()

        _func.__name__ = func.__name__
        _func.__doc__ = func.__doc__

        return _func

    return dec