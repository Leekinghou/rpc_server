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

from tornado.ioloop import IOLoop

from beehive.libs.pyrestful.rest import RestService
from beehive.server.api.crack import CrackHandler
from beehive.server.rpc_server import BeetleRPCServer


class BeetleServer(object):

    def __init__(self, rpc_host, rpc_port, api_host, api_port):
        self.ioloop = IOLoop.current()
        self.rpc_server = BeetleRPCServer(rpc_host, rpc_port)
        self.rest_app = RestService(
            [CrackHandler], dict(rpc_server=self.rpc_server)
        )
        self.api_host = api_host
        self.api_port = api_port
        self.logger = logging.getLogger('BeetleServer')

    def run(self):
        self.logger.info('BeetleServer starts')
        self.rpc_server.run()
        self.rest_app.listen(self.api_port, address=self.api_host)
        self.logger.info(
            'API Service listen to: (%s, %s)', self.api_host, self.api_port
        )
        self.ioloop.start()
        self.logger.info('BeetleServer stopped')

