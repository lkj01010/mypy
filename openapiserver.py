# -*- coding: UTF-8 -*-
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json
from log import server_log
import cfg
from openapi import openapi_v3


def pretty_show(jdata):
    print json.dumps(jdata, indent=4, ensure_ascii=False).encode('utf8')

from tornado.options import define, options
define("port", default=12303, help="run on the given port", type=int)
#######################################################################

class Application(tornado.web.Application):
    APP_ID = 1104680669
    APP_KEY = 'M6TOzozadY9AK8ug'
    SERVER_LIST = ('openapi.tencentyun.com',)
    ZONE_ID = '1'

    def __init__(self):
        handlers = [
            (r"/", ApiHandler)
        ]
        self.api = openapi_v3.OpenAPIV3(Application.APP_ID,
                                        Application.APP_KEY,
                                        Application.SERVER_LIST)

        self.notify_client = tornado.httpclient.AsyncHTTPClient()
        tornado.web.Application.__init__(self, handlers, debug=True)

    def push_billinfo_to_db(self, openid, user_pf, bill_dict):
        """
        the return bill dict is like this:
        {'code':0, 'default':0, 'subcode':0, 'message':'',
            'data': [ {'billno': '-3138_A50009_1_1442038070_5357735', 'cost':8} ]
        }
        """
        if bill_dict['code'] == 0:  # pay success
            bill_dict['data'][0]['user_id'] = openid
            bill_dict['data'][0]['user_pf'] = user_pf
            data_str = json.JSONEncoder().encode(bill_dict['data'][0])
            # bill_str = json.dumps(bill_dict, indent=4, ensure_ascii=False).encode('utf8')
            request = tornado.httpclient.HTTPRequest(
                'http://' + cfg.DB_SERVER_ADDR + ':' + str(cfg.DB_SERVER_PORT) + '/billinfo',
                method='POST', body=data_str)
            self.notify_client.fetch(request, callback=Application.push_billinfo_to_db_callback)

    @staticmethod
    def push_billinfo_to_db_callback(response):
        print 'push billinfo ret:', response.body

class ApiHandler(tornado.web.RequestHandler):

    def get(self):
        print 'api uri:', self.request.uri
        server_log.info('api uri:' + self.request.uri)
        try:
            openid = self.get_argument('openid')
            openkey = self.get_argument('openkey')
            platform = self.get_argument('platform')
            api = self.get_argument('api')
            callback = self.get_argument('callback')
        except KeyError:
            server_log.warning("except KeyError: Failed to get argument", exc_info=True)

        server_log.info('handle api:' + api)
        replay = ''
        if api == 'k_userinfo':
            jdata = self.application.api.call('/v3/user/get_info', {
                'openid': openid,
                'openkey': openkey,
                'pf': platform,
            })
            jdata['is_ok'] = 1
            jdata['openid'] = openid
            jdata['openkey'] = openkey
            # replay = json.JSONEncoder().encode(jdata)
            replay = json.dumps(jdata, ensure_ascii=False).encode('utf8')
        elif api == 'k_playzone_userinfo':
            jdata = self.application.api.call('/v3/user/get_playzone_userinfo', {
                'openid': openid,
                'openkey': openkey,
                'pf': platform,
                'zoneid': Application.ZONE_ID
            })
            jdata['is_ok'] = 1
            jdata['openid'] = openid
            jdata['openkey'] = openkey
            replay = json.dumps(jdata, ensure_ascii=False).encode('utf8')
        elif api == 'k_buy_playzone_item':
            itemid = self.get_argument('itemid')
            count = self.get_argument('count')
            user_pf = self.get_argument('user_pf')
            jdata = self.application.api.call('/v3/user/buy_playzone_item', {
                'openid': openid,
                'openkey': openkey,
                'pf': platform,
                'zoneid': Application.ZONE_ID,
                'itemid': itemid,
                'count': count
            })
            jdata['is_ok'] = 1
            replay = json.dumps(jdata, ensure_ascii=False).encode('utf8')
            self.application.push_billinfo_to_db(openid, user_pf, jdata)
        else:
            replay = "{'is_ok':0, 'msg': 'invalid api'}"

        print replay
        # lkj bug: how to show unicode - chinese
        replay = callback.encode('utf8') + '(' + replay + ')'
        self.write(replay)

if __name__ == "__main__":
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
