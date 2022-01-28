#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
    __init__.py.py
      ~~~~~

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 18:51
    @python version: 3.8
"""



import logging
import random
import sys
import time

from six.moves import cPickle as pickle
from tornado import gen
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer
from tornado.web import Application

from beehive.libs.signal_helper import add_shutdown_handler
from beehive.message import RPCException, RPCMessage, RPCRequest, RPCResponse


def rpc(func):
    func_name = func.__name__

    def _func(self, *args, **kwargs):
        timeout = kwargs.get('timeout', 30)
        time_start = time.time()
        while self.stream.reading() or self.stream.writing():
            if time.time() - time_start > timeout:
                raise Exception('RPC waiting timeout')
            yield gen.sleep(0.1)

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
        except StreamClosedError as e:
            self.server.deregister(self)
            raise e
        except Exception as e:
            raise e

        if isinstance(res, RPCException):
            raise Exception(res['value'])

        raise gen.Return(res['value'])

    _func.__name__ = func_name

    return _func


class RemoteClient(object):

    EOM = b'BEETLE_EOM'

    def __init__(self, server, stream, address, client_type=None):
        self.server = server
        self.stream = stream
        self.address = address
        self.client_type = client_type

    @gen.coroutine
    @rpc
    def heart_beat(self):
        pass

    @gen.coroutine
    @rpc
    def crack(self, *args, **kwargs):
        pass


class BeetleRPCServer(TCPServer):
    """
    Beetle cookie pool rpc server side
    """

    EOM = b'BEETLE_EOM'

    def __init__(self, host, port):
        super(BeetleRPCServer, self).__init__()
        self.host = host
        self.port = port
        self.logger = logging.getLogger('BeetleRPCServer')

        self.registered_clients = []
        self.address_map = {}

        self.ioloop = IOLoop.current()
        self._is_exiting = False
        self._is_running = False
        self._type_name = type(self).__name__

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

    def run(self):
        try:
            self.logger.info(self._type_name + ' starts')
            self.ioloop.make_current()
            self.listen(self.port, self.host)
            self._is_running = True
        except Exception as e:
            self.logger.exception(e)

    @gen.coroutine
    def handle_stream(self, stream, address):
        self.logger.info('Client connected: %s', address)
        remote_client = RemoteClient(self, stream, address)
        server = self

        def close_callback():
            server.deregister(remote_client)

        stream.set_close_callback(close_callback)

        self.address_map[address] = remote_client
        while remote_client not in self.registered_clients:
            try:
                self.logger.info('Waiting for Registeration')
                req = yield stream.read_until(self.EOM)
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
                try:
                    res = yield gen.maybe_future(
                        self.__getattribute__(func_name)(
                            remote_client, *args, **kwargs
                        )
                    )
                    res = RPCResponse(res)
                except Exception as e:
                    self.logger.exception(e)
                    res = RPCException(str(e))
                yield stream.write(
                    pickle.dumps(dict(res), protocol=2) + self.EOM
                )
            except StreamClosedError:
                self.deregister(remote_client)
                break

    @gen.coroutine
    def register(self, remote_client, client_type):
        remote_client.client_type = client_type
        if remote_client not in self.registered_clients:
            self.registered_clients.append(remote_client)
        self.logger.info('Stream registered: %s', remote_client.address)
        raise gen.Return(True)

    def deregister(self, remote_client):
        del self.address_map[remote_client.address]
        self.registered_clients.remove(remote_client)
        self.logger.info('Stream degistered: %s', remote_client.address)

    def get_random_client(self, client_type):
        clients = [
            client for client in self.registered_clients
            if client.client_type == client_type
        ]
        if not clients:
            return None
        return random.choice(clients)
