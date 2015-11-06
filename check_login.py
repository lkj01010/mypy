import tornado.httpclient
import tornado.ioloop
from log import server_log
import json
import cfg


class LoginChecker(object):

    # !!! user has multi keys when login multi device , we cache all these keys, neither we will check them endlessly
    user_cache = dict()
    _CLEANUP_INTERVAL = 3600 * 1000

    def __init__(self):
        self.chk_client = tornado.httpclient.AsyncHTTPClient()
        self.check_ret_callback = None
        time_task = tornado.ioloop.PeriodicCallback(self._clean_up, LoginChecker._CLEANUP_INTERVAL)
        time_task.start()

    @staticmethod
    def _clean_up():
        LoginChecker.user_cache = dict()

    def check_info(self, user_id, user_key, zoneid, callback):
        self.check_ret_callback = callback

        if cfg.IS_REMOTE == 0:
            self.check_ret_callback(True)
        else:
            is_need_check = False
            if user_id in LoginChecker.user_cache.keys():
                if user_key in LoginChecker.user_cache[user_id]:
                    server_log.warn('check ok, account in cache')
                    self.check_ret_callback(True)
                else:
                    is_need_check = True
            else:
                '''insure key-set in user_cache'''
                LoginChecker.user_cache[user_id] = set()
                server_log.warn('user_cache len: %d, user add: %s' % (len(LoginChecker.user_cache), user_id))
                is_need_check = True

            if is_need_check:
                server_log.info('need check_info, user_id = ' + user_id + 'user_key = ' + user_key)
                '''should check from tencent server'''
                request = tornado.httpclient.HTTPRequest(cfg.TENCENT_ACCOUNT_SERVER +
                                                         '/?openid=' + user_id +
                                                         '&openkey=' + user_key +
                                                        '&user_pf=' + zoneid +
                                                        '&api=k_playzone_userinfo' +
                                                         '&platform=qzone' +
                                                        '&callback=cb',
                                                        method='GET')
                server_log.info('new active url: ' + request.url)
                self.chk_client.fetch(request, callback=self._check_response_callback)

    def _check_response_callback(self, response):
        server_log.info('check_callback: ' + str(response.body))

        is_valid = False
        if response and response.body:
            j_body = json.JSONDecoder().decode(response.body.lstrip('cb(').rstrip(')'))

            if 'data'in j_body and j_body['is_ok'] == 1 and 'openid' in j_body and 'openkey' in j_body:
                openid = j_body['openid']
                if openid in LoginChecker.user_cache:
                    pass
                else:
                    LoginChecker.user_cache[openid] = set()
                LoginChecker.user_cache[openid].add(j_body['openkey'])
                is_valid = True

                # '''hold a max number of active accounts'''
                # if len(LoginChecker.user_expire_holder) > 10000:
                #     expired = LoginChecker.user_expire_holder.pop(0)
                #     if expired:
                #         server_log.error('expired: ' + expired)
                #         del LoginChecker.user_cache[expired]

        self.check_ret_callback(is_valid)

if __name__ == "__main__":
    app = LoginChecker()
    app.check_info('B1D43980E13A9C90F74F2C7405AE54A8', 'KFEJIFEIEKKFEJF012912', 1)
    tornado.ioloop.IOLoop.instance().start()
