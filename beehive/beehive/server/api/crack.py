#!/usr/bin/env python 
# -*- coding: utf-8 -*-
"""
    crack.py
      ~~~~~

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 20:42
    @python version: 3.8
"""


from tornado import gen

from beehive.libs.pyrestful import mediatypes
from beehive.libs.pyrestful.rest import delete, get, post, put

from . import BaseRequestHandler


class Error(object):
    WRONG_PARAMETER = {'err': 1000, 'msg': 'Wrong parameter'}
    CRACKER_NOT_FOUND = {'err': 1001, 'msg': 'Cracker not found'}
    SERVER_ERROR = {'err': 1002, 'msg': 'Server error'}


class CrackHandler(BaseRequestHandler):

    @post(
        path='/api/crack/{cracker_type}',
        produces=mediatypes.APPLICATION_JSON,
    )
    @gen.coroutine
    def crack(self, cracker_type):
        """
        ## Crack

            POST '/api/crack/<cracker_type>'
        """

        arguments = self.request.arguments
        files = self.request.files
        params = {}
        params.update(arguments)
        params.update(files)

        cracker_client = self.rpc_server.get_random_client(cracker_type)

        if not cracker_client:
            raise gen.Return(self.gen_http_error(404, Error.CRACKER_NOT_FOUND))

        try:
            ret = yield cracker_client.crack(params)
        except Exception as e:
            self.logger.exception(e)
            raise gen.Return(self.gen_http_error(500, Error.SERVER_ERROR))

        raise gen.Return({'ret': ret})
