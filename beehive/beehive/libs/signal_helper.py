# -*- coding: utf-8 -*-
"""
    signal_helper.py
    ~~~~~~~~~~~~~~

    signal helper

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 20:44
    @python version: 3.8
"""

import signal

_HANDLERS = []


def _handler(*args):
    """Real handler"""
    for handler in _HANDLERS:
        handler(*args)


signal.signal(signal.SIGTERM, _handler)
signal.signal(signal.SIGINT, _handler)


def add_shutdown_handler(sig_handler):
    """Add a sig hander"""
    _HANDLERS.append(sig_handler)
