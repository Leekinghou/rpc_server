#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
    __init__.py.py
      ~~~~~

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 20:46
    @python version: 3.8
"""




class MessageType(object):
    Exception = 0
    Request = 1
    Response = 2


class RPCMessage(dict):

    @classmethod
    def from_dict(cls, data):
        msg_type = data.get('msg_type')
        value = data.get('value')
        if msg_type == MessageType.Request:
            return RPCRequest(value['func'], value['args'], value['kwargs'])
        elif msg_type == MessageType.Response:
            return RPCResponse(value)
        elif msg_type == MessageType.Exception:
            return RPCException(value)
        return None

    def __init__(self, msg_type, value):
        self['msg_type'] = msg_type
        self['value'] = value


class RPCRequest(RPCMessage):

    def __init__(self, func, args, kwargs):
        super(RPCRequest, self).__init__(
            MessageType.Request,
            {
                'func': func,
                'args': args,
                'kwargs': kwargs,
            },
        )


class RPCResponse(RPCMessage):

    def __init__(self, value):
        super(RPCResponse, self).__init__(
            MessageType.Response,
            value,
        )


class RPCException(RPCMessage):

    def __init__(self, execption):
        super(RPCException, self).__init__(
            MessageType.Exception,
            execption,
        )
