#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
    __init__.py.py
      ~~~~~

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 20:47
    @python version: 3.8
"""

import logging
import sys

from six.moves import cPickle as pickle
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.tcpclient import TCPClient

from beehive.libs.signal_helper import add_shutdown_handler
from beehive.message import RPCException, RPCMessage, RPCRequest, RPCResponse


def rpc(func):
    func_name = func.__name__

    def _func(self, *args, **kwargs):
        if not self._connected:
            yield self.connect()
            if not self._connected:
                raise Exception('Connection Error')

        req = pickle.dumps(RPCRequest(func_name, args, kwargs), protocol=2)

        res = None
        try:
            yield self.stream.write(req + self.EOM)
            res = yield self.stream.read_until(self.EOM)
            if sys.version_info.major > 2:
                res = pickle.loads(res[:-len(self.EOM)], encoding='latin1')
            else:
                res = pickle.loads(res[:-len(self.EOM)])
            res = RPCMessage.from_dict(res)
        except Exception as e:
            self._connected = False
            raise e

        if isinstance(res, RPCException):
            raise Exception(res['value'])

        raise gen.Return(res['value'])

    _func.__name__ = func_name

    return _func


class BeetleRPCClient(object):
    """
    BeetleRPCClient to connect to BeetleRPCServer
    """

    EOM = b'BEETLE_EOM'
    _type_name = 'BeetleRPCClient'

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.logger = logging.getLogger('BeetleRPCClient')
        self.stream = None
        self._connected = False
        self._registered = False

        self.ioloop = IOLoop.current()
        self._is_exiting = False
        self._is_running = False

        add_shutdown_handler(self.shutdown)

    def shutdown(self, sig, frame):
        """Handle shutdown signal"""
        if self._is_exiting is True:
            return

        self._is_exiting = True
        self.ioloop.add_callback(self.before_exit)
        self.logger.info('Caught signal: %s', sig)

    @gen.coroutine
    def before_exit(self):
        """Do clean up jobs"""
        self.logger.info(self._type_name + ' stopping')
        try:
            yield gen.maybe_future(self.on_before_exit())
        except Exception as e:
            self.logger.exception(e)

        if self._is_running:
            self.ioloop.stop()
            self._is_running = False
        else:
            self.logger.warning(self._type_name + ' not running')

    def on_before_exit(self):
        """Do clean up jobs"""
        pass

    @gen.coroutine
    def connect(self):
        """
        连接并注册到远程服务器
        """

        if self._registered:
            return

        max_connect_times = 3
        connect_times = 0
        while connect_times <= max_connect_times:
            try:
                if not self._connected:
                    self.logger.info('Connecting...')
                    self.stream = yield TCPClient().connect(
                        host=self.host, port=self.port
                    )
                    self.logger.info('Connected')
                    self._connected = True
                if not self._registered:
                    self.logger.info('Registing...')
                    ret = yield self.register(self._type_name)
                    if ret:
                        self._registered = True
                        self.logger.info('Registered')
                break
            except StreamClosedError as e:
                # Try reconnecting
                self.logger.info('Connection Failed')
                self._connected = False
                self._registered = False
                connect_times += 1
                yield gen.sleep(1)

    @gen.coroutine
    @rpc
    def register(self, client_type):
        """
        注册客户端类型 RPC 方法（不需要实现）
        """
        pass

    def heart_beat(self):
        return True

    def run(self):
        try:
            self.logger.info(self._type_name + ' starts')
            self.ioloop.make_current()
            self.main_loop()
            self.ioloop.start()
        except Exception as e:
            self.logger.exception(e)
        self.logger.info(self._type_name + ' stopped')

    @gen.coroutine
    def main_loop(self):
        """
        主循环逻辑
        """
        self._is_running = True

        while True:
            try:
                if not self._registered:
                    yield self.connect()
                if not self._registered:
                    continue
                self.logger.info('Waiting For Request...')
                req = yield self.stream.read_until(self.EOM)
                req = req[:-len(self.EOM)]
                if sys.version_info.major > 2:
                    req = pickle.loads(req, encoding='latin1')
                else:
                    req = pickle.loads(req)

                req = RPCMessage.from_dict(req)
                data = req['value']
                func_name = data['func']
                args = data['args']
                kwargs = data['kwargs']
                self.logger.info('RPC Called: ' + func_name)
                try:
                    res = yield gen.maybe_future(
                        self.__getattribute__(func_name)(*args, **kwargs)
                    )
                    res = RPCResponse(res)
                except Exception as e:
                    self.logger.exception(e)
                    res = RPCException(str(e))
                yield self.stream.write(
                    pickle.dumps(dict(res), protocol=2) + self.EOM
                )
            except StreamClosedError:
                self._connected = False
                self._registered = False
                yield self.connect()
