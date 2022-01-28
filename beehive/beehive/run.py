#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
    run.py
      ~~~~~

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 18:50
    @python version: 3.8
"""

import logging.config
import os
import random
import sys
import time

import click
import yaml

from beehive.server import BeetleServer

lib_path = os.path.dirname(__file__)
logging.config.fileConfig(os.path.join(lib_path, 'logging.conf'))


def load_config(config_path):
    with open(os.path.join(lib_path, 'config/default_config.yml'), 'r') as f:
        config = yaml.load(f)
    with open(config_path, 'r') as f:
        config.update(yaml.load(f))
    return config


@click.group()
@click.option(
    '--config-file',
    '-c',
    default=os.path.join(lib_path, 'config/default_config.yml')
)
@click.pass_context
def cli(ctx, config_file):
    ctx.obj = {'config': load_config(config_file)}


@cli.command()
@click.pass_context
def server(ctx):

    config = ctx.obj['config']

    # rpc_server

    inst = BeetleServer(
        rpc_host=config['rpc_host'],
        rpc_port=config['rpc_port'],
        api_host=config['api_host'],
        api_port=config['api_port'],
    )

    inst.run()
