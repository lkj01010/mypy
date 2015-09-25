import tornado.httpclient
import tornado.ioloop
from log import server_log
import json
import cfg


class LoginChecker(object):

    # !!! user has multi keys when login multi device , we cache all these keys, neither we will check them endlessly
    user_cache = dict()
    user_expire_holder = list()

    def __init__(self):
        self.chk_client = tornado.httpclient.AsyncHTTPClient()
        self.check_ret_callback = None

    def check_info(self, user_id, user_key, zoneid, callback):
        self.check_ret_callback = callback

        is_need_check = False
        if user_id in LoginChecker.user_cache.keys():
            if user_key in LoginChecker.user_cache[user_id]:
                server_log.warn('WA!!!!!!! in it !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                self.check_ret_callback(True)
            else:
                is_need_check = True
        else:
            '''insure key-set in user_cache'''
            LoginChecker.user_cache[user_id] = set()
            is_need_check = True

        if is_need_check:
            server_log.info('need check_info, user_id = ' + user_id, 'user_key = ' + user_key)
            '''should check from tencent server'''
            request = tornado.httpclient.HTTPRequest(cfg.TENCENT_ACCOUNT_SERVER +
                                                     '?openid=' + user_id +
                                                     '&openkey=' + user_key +
                                                    '&user_pf=' + zoneid +
                                                    '&api=k_playzone_userinfo' +
                                                     '&platform=qzone' +
                                                    '&callback=cb',
                                                    method='GET')
            server_log.info('new active url: ' + request.url)
            self.chk_client.fetch(request, callback=self._check_response_callback)
            return False

    def _check_response_callback(self, response):
        # server_log.info('check_callback: ' + str(response.body))
        if response and response.body:
            j_body = json.JSONDecoder().decode(response.body.lstrip('cb(').rstrip(')'))
            if j_body['is_ok'] == 1 and 'openid' in j_body and 'openkey' in j_body:
                openid = j_body['openid']

                server_log.warn('1 user_cache len: %d' % len(LoginChecker.user_cache))
                LoginChecker.user_cache[openid].add(j_body['openkey'])
                server_log.warn('2 user_cache len: %d' % len(LoginChecker.user_cache))

                server_log.warn('user_cache push: ' + openid)
                LoginChecker.user_expire_holder.append(openid)
                self.check_ret_callback(True)
                '''hold a max number of active accounts'''
                if len(LoginChecker.user_expire_holder) > 10000:
                    expired = LoginChecker.user_expire_holder.pop(0)
                    if expired:
                        server_log.error('expired: ' + expired)
                        del LoginChecker.user_cache[expired]
            return

        # local test allow all account
        if cfg.IS_REMOTE:
            self.check_ret_callback(False)
        else:
            self.check_ret_callback(True)

if __name__ == "__main__":
    app = LoginChecker()
    app.check_info('B1D43980E13A9C90F74F2C7405AE54A8', 'KFEJIFEIEKKFEJF012912', 1)
    tornado.ioloop.IOLoop.instance().start()
