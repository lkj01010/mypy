import tornado.httpclient
import tornado.ioloop
from log import server_log
import json

# TENCENT_ACCOUNT_SERVER = 'http://127.0.0.1:12303/'
TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303/'

class CheckLogin(object):
    def __init__(self):
        self.user_cache = dict()
        # self.user_expire_holder = [None] * 10000
        self.user_expire_holder = []
        self.chk_client = tornado.httpclient.AsyncHTTPClient()
        self.read_callback = None
        self.read_callback_invoker = None
        self.write_callback = None
        self.write_callback_invoker = None

    def check_info(self, user_id, user_key, is_read):
        # if user_id in self.user_cache:
        if user_id in self.user_cache and self.user_cache[user_id] == user_key:
            return True
        else:
            if is_read:
                callback = self._read_callback
            else:
                callback = self._write_callback

            '''should check from tencent server'''
            request = tornado.httpclient.HTTPRequest(TENCENT_ACCOUNT_SERVER +
                                                     'openid='+ user_id +
                                                     '&openkey=' + user_key +
                                                    '&api=k_userinfo' +
                                                     '&platform=wanba_ts' +
                                                    '&callback=cb',
                                                    method='GET')
            print request.url
            server_log.info('new active url: ' + request.url)
            self.chk_client.fetch(request, callback=callback)
            return False

    def _write_callback(self, response):
        self._inner_callback(response, self.write_callback, self.write_callback_invoker)

    def _read_callback(self, response):
        self._inner_callback(response, self.read_callback, self.read_callback_invoker)

    def _inner_callback(self, response, cb, cb_invoker):
        server_log.info('check_callback' + str(response.body))
        j_body = json.JSONDecoder().decode(response.body.lstrip('cb(').rstrip(')'))
        if j_body['is_ok'] == 0 and 'openid' in j_body and 'openkey' in j_body:
            openid = j_body['openid']
            self.user_cache[openid] = j_body['openkey']
            self.user_expire_holder.append(openid)
            cb(openid, True)
            '''hold a max number of active accounts'''
            if len(self.user_expire_holder) > 10000:
                expired = self.user_expire_holder.pop(0)
                if expired:
                    del self.user_cache[expired]
        else:
            cb(None, False)

if __name__ == "__main__":
    app = CheckLogin()
    app.check_info('B1D43980E13A9C90F74F2C7405AE54A8', 'KFEJIFEIEKKFEJF012912')
    tornado.ioloop.IOLoop.instance().start()
