# -*- coding: utf-8 -*-
"""
    time_helper.py
    ~~~~~~~~~~~~~~

    @Author  : lijinhao
    @copyright: (c) 2021 Baikal
    @date created: 2022/1/25 20:44
    @python version: 3.8
"""

import sys
import base64
import json
from datetime import datetime
from json.encoder import (
    INFINITY, JSONEncoder, _make_iterencode, c_make_encoder, encode_basestring,
    encode_basestring_ascii
)

from bson.objectid import ObjectId

from .time_helper import datetime2timestamp


class ByteEncoder(JSONEncoder):
    # def default(self, o):
    #     if isinstance(o, str):
    #         try:
    #             o.decode('utf-8')
    #         except UnicodeDecodeError:
    #             o = BYTE_PREFIX + base64.encodestring(o)
    #     return super(ByteEncoder, self).default(o)

    def iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string
        representation as available.
        For example::
            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)
        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring

        def _encoder(o, _orig_encoder=_encoder, _encoding='utf-8'):  # pylint: disable=E0102
            if isinstance(o, str) and sys.version < '3':
                try:
                    o.decode(_encoding)
                except UnicodeDecodeError:
                    o = BYTE_PREFIX + base64.encodestring(o)
            elif isinstance(o, bytes):
                o = BYTE_PREFIX + base64.encodestring(o)
            return _orig_encoder(o)

        def floatstr(
            o,
            allow_nan=self.allow_nan,
            _repr=float.__repr__,
            _inf=INFINITY,
            _neginf=-INFINITY
        ):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o)
                )

            return text

        if (_one_shot and c_make_encoder is not None and self.indent is None):
            _iterencode = c_make_encoder(
                markers, self.default, _encoder, self.indent,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, self.allow_nan
            )
        else:
            _iterencode = _make_iterencode(
                markers, self.default, _encoder, self.indent, floatstr,
                self.key_separator, self.item_separator, self.sort_keys,
                self.skipkeys, _one_shot
            )
        return _iterencode(o, 0)


class JsonEncoder(ByteEncoder):

    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, datetime):
            return datetime2timestamp(obj)
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, bytes):
            return BYTE_PREFIX + base64.encodebytes(obj).decode()
        else:
            return json.JSONEncoder.default(self, obj)


def ensure_utf_8(string):
    """ensure string to be utf-8 encoded"""
    if isinstance(string, unicode):
        return string.encode('utf-8')
    return string


def format_json(obj):
    return json.loads(json.dumps(obj, cls=JsonEncoder))


BYTE_PREFIX = '[BEETLE_BYTES]'


def stringify_json(obj):
    """dict to utf-8 json str"""
    return ensure_utf_8(json.dumps(obj, ensure_ascii=False, cls=JsonEncoder))


def parse_json(json_str):
    """str to UTF-8 dict"""
    return json.loads(json_str, object_hook=_decode_dict, strict=False)


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        elif isinstance(item, str) and item.startswith(BYTE_PREFIX):
            item = base64.decodestring(item[len(BYTE_PREFIX):])
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        elif isinstance(value, str) and value.startswith('[VENOM_BYTES]'):
            value = base64.decodestring(value[len('[VENOM_BYTES]'):])
        rv[key] = value
    return rv
