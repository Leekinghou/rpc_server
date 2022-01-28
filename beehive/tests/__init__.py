#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description of this file
    
    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 18:49
    @python version: 3.8
"""

import sys
import os
import logging.config

lib_path = os.path.dirname(__file__)
logging.config.fileConfig(os.path.join(lib_path, '../beetle/logging.conf'))