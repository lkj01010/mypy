# -*- coding: UTF-8 -*-
import httplib
import urllib
# import os
# import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/' + '..')
# import cfg
import json

http_client = None
try:
    http_client = httplib.HTTPConnection('127.0.0.1', 13001, timeout=30)

    body = dict()
    body['type'] = 0
    body['msg'] = "服务器正在维护，预计12:10恢复正常，给您带来不便，深表歉意"
    body_json = json.JSONEncoder().encode(body)
    print 'send cmd: ', body_json

    params = urllib.urlencode({'cmd': body_json})
    print 'params:', params
    http_client.request('GET', '/cmd?' + params)

    response = http_client.getresponse()
    print response.status
    print response.reason
    print response.read()
except Exception, e:
    print e
finally:
    if http_client:
        http_client.close()
