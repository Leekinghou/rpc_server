#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    test_rpc.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description of this file
    
    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 18:49
    @python version: 3.8
"""

from tornado import gen
from tornado.testing import AsyncTestCase, gen_test

from beehive.client import BeetleRPCClient
from beehive.server.rpc_server import BeetleRPCServer
from beehive.utils import run_in_thread, run_in_subprocess


class TestRPC(AsyncTestCase):

    test_host = '127.0.0.1'
    test_port = 10888
    test_source = 'test_source'

    @classmethod
    def setUpClass(cls):
        cls.server = BeetleRPCServer(
            cls.test_host,
            cls.test_port,
        )
        cls.server_thread = run_in_thread(cls.server.run)
        cls.client = BeetleRPCClient(
            cls.test_host,
            cls.test_port,
        )
        cls.client_thread = run_in_thread(cls.client.run)

    @classmethod
    def tearDownClass(cls):
        cls.client.ioloop.stop()
        cls.server.ioloop.stop()

    @gen_test
    def test_connection(self):
        while not self.client._registered:
            yield gen.sleep(0.1)
        self.assertTrue(self.server.registered_clients)

    @gen_test
    def test_rpc(self):
        while not self.client._registered:
            yield gen.sleep(0.1)

        remote_client = self.server.registered_clients[0]

        ret = yield remote_client.heart_beat()
        self.assertTrue(ret)