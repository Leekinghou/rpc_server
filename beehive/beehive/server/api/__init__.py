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

from beehive.libs.pyrestful.rest import RestHandler


class BaseRequestHandler(RestHandler):

    def initialize(self, rpc_server):
        self.rpc_server = rpc_server
        self.logger = logging.getLogger('api')