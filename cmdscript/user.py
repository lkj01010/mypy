# -*- coding: UTF-8 -*-
import tornado.options
import httplib
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/' + '..')
print 'dir __file__', os.path.abspath(__file__)
print 'append ', os.path.dirname(os.path.abspath(__file__)) + '/' + '..'
import cfg
import json
"""why can't import mypy ???
"""
from tornado.options import define, options


define("cmd", default='', help="cmd: kick who, unkick who", type=str)
define("user_uid", default='', help="user_uid", type=str)


def run_cmd():
    http_client = None
    try:
        http_client = httplib.HTTPConnection('localhost', cfg.RECORD_SERVER_PORT, timeout=30)

        body = dict()
        if options.cmd == 'kick':
            body['cmd'] = 'kick'
            body['param'] = dict()
            body['param']['user_uid'] = options.user_uid
        elif options.cmd == 'unkick':
            body['cmd'] = 'unkick'
            body['param'] = dict()
            body['param']['user_uid'] = options.user_uid

        body_json = json.JSONEncoder().encode(body)
        print 'send cmd', body_json
        http_client.request('POST', '/cmd', body_json)

        response = http_client.getresponse()
        print response.status
        print response.reason
        print response.read()
    except Exception, e:
        print e
    finally:
        if http_client:
            http_client.close()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    run_cmd()