import tornado.httpclient
import tornado.ioloop
from log import server_log
import time
import check_login

TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'

class CheckLoginTest:
    def __init__(self):
        # AsyncHTTPClient is one per IOLoop
        chk_client1 = tornado.httpclient.AsyncHTTPClient()
        chk_client2 = tornado.httpclient.AsyncHTTPClient()
        chk_client3 = tornado.httpclient.HTTPClient()
        chk_client4 = tornado.httpclient.HTTPClient()

        self.cache = list()
        pass

    def test(self):
        for i in range(100):
            user_id = 'userid' + str(i)
            user_key = 'userkey' + str(i)

            chk_client = tornado.httpclient.HTTPClient()
            request1 = tornado.httpclient.HTTPRequest(TENCENT_ACCOUNT_SERVER +
                                                     '/?openid=' + user_id +
                                                     '&openkey=' + user_key +
                                                    '&api=k_userinfo' +
                                                     '&platform=wanba_ts' +
                                                    '&callback=cb',
                                                    method='GET')
            response = chk_client.fetch(request1, callback=CheckLoginTest._test_callback)
            print 'send request url: ', request1.url

    @staticmethod
    def _test_callback(response):
        print 'response: ', response.body

    def check_login_checker(self):
        for i in range(100):
            checker = check_login.LoginChecker()
            user_id = 'userid' + str(i)
            user_key = 'userkey' + str(i)
            checker.check_info(user_id, user_key, self._test_callback)

if __name__ == "__main__":

    dict = {'Name': 'Zara', 'Age': {'xx':1}}
    dict2 = {'Age': {'ffff': 'female' }}

    dict.update(dict2)
    print "Value : %s" %  dict


    app = CheckLoginTest()
    # app.test()
    app.check_login_checker()
    tornado.ioloop.IOLoop.instance().start()
