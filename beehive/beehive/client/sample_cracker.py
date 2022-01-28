#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
    sample_cracker.py
      ~~~~~

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 20:48
    @python version: 3.8
"""


from beehive.client import BeetleRPCClient


class SampleCrackerClient(BeetleRPCClient):

    _type_name = 'sample'

    def crack(self, *args, **kwargs):
        # do some crack
        return args
