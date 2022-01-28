#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
    test_crack_api.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description of this file
    
    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 18:49
    @python version: 3.8
"""

import mimetypes

from tornado import gen
from tornado.testing import AsyncTestCase, gen_test
from tornado.httpclient import HTTPRequest
from tornado.httpclient import AsyncHTTPClient

from beehive.client.sample_cracker import SampleCrackerClient
from beehive.server import BeetleServer
from beehive.utils import run_in_thread, run_in_subprocess


def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files.
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = b'----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields:
        L.append(b'--' + BOUNDARY)
        L.append(b'Content-Disposition: form-data; name="%s"' % key.encode())
        L.append(b'')
        L.append(value.encode() if isinstance(value, str) else value)
    for (key, filename, value) in files:
        filename = filename.encode("utf8")
        L.append(b'--' + BOUNDARY)
        L.append(
            b'Content-Disposition: form-data; name="%s"; filename="%s"' %
            (key.encode(), filename)
        )
        L.append(b'Content-Type: %s' % get_content_type(filename).encode())
        L.append(b'')
        L.append(value.encode() if isinstance(value, str) else value)
    L.append(b'--' + BOUNDARY + b'--')
    L.append(b'')
    body = CRLF.join(L)
    content_type = b'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


def get_content_type(filename):
    return mimetypes.guess_type(filename.decode()
                                )[0] or 'application/octet-stream'


class TestCrackerAPI(AsyncTestCase):

    test_host = '127.0.0.1'
    test_port = 10888
    test_api_host = '127.0.0.1'
    test_api_port = 10999

    @classmethod
    def setUpClass(cls):
        cls.server = BeetleServer(
            cls.test_host,
            cls.test_port,
            cls.test_api_host,
            cls.test_api_port,
        )
        cls.server_thread = run_in_thread(cls.server.run)
        cls.client = SampleCrackerClient(
            cls.test_host,
            cls.test_port,
        )
        cls.client_thread = run_in_thread(cls.client.run)
        cls.fetcher = AsyncHTTPClient()

    @classmethod
    def tearDownClass(cls):
        cls.client.ioloop.stop()
        cls.server.ioloop.stop()

    @gen_test
    def test_api(self):
        while not self.client._registered:
            yield gen.sleep(0.1)

        with open('tests/test.png', 'rb') as fin:
            img = fin.read()

        content_type, body = encode_multipart_formdata(
            fields=[
                ('param1', '1'),
                ('param2', 'str'),
            ],
            files=[
                ('file1', 'test.png', img),
            ]
        )

        res = yield self.fetcher.fetch(
            HTTPRequest(
                url='http://{}:{}/api/crack/sample'.format(
                    self.test_api_host, self.test_api_port
                ),
                method='POST',
                headers={
                    'Content-Type': content_type,
                },
                body=body,
            )
        )

        print(res.body)

        self.assertTrue(res.code == 200)