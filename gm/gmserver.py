# -*- coding: UTF-8 -*-
import os.path
import random

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import pymongo
from log import server_log

from tornado.options import define, options

define("db_addr", default="203.195.243.33", help="db addr", type=str)
define("db_port", default=27017, help="db port", type=int)
define("port", default=8012, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r'/', IndexHandler),
                    (r'/login', LoginHandler),
                    (r'/userDetail', UserDetailHandler),
                    (r'/userDetail/changeGold', UserDetailChangeGoldHandler),
                    (r'/userDetail/changeZuan', UserDetailChangeZaunHandler),
                    (r'/test', TestHandler)]

        server_log.info('gm server start on db[' + options.db_addr + ':' + str(options.db_port) + ']')

        conn = pymongo.MongoClient(options.db_addr, options.db_port)
        self.db = conn['dota']

        tornado.web.Application.__init__(self,
                                        handlers,
                                        template_path=os.path.join(os.path.dirname(__file__), "templates"),
                                        static_path=os.path.join(os.path.dirname(__file__), "static"),
                                        ui_modules={'UserData': UserDataModule},
                                        debug=True)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('login.html')

class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        self.render('user_query.html')

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index_login.html')

class UserDetailHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index_login.html')

    def post(self):
        userno = self.get_argument('userno')
        user_data = self.application.db.user.find_one({'record.userno': userno})
        ret_msg = str()
        if not user_data or len(user_data) == 0:
           ret_msg = u"没有该用户"
        else:
           ret_msg = u"用户编号：" + userno
        if not user_data:
            user_data = dict()
        self.render('user_query_detail.html', ret_msg=ret_msg, data=user_data)

class UserDetailChangeGoldHandler(tornado.web.RequestHandler):
    def post(self):
        gold = self.get_argument('changeGold')
        user_data = self.application.db.user.update({'record.userno': userno})
        ret_msg = str()
        if not user_data or len(user_data) == 0:
           ret_msg = u"没有该用户"
        else:
           ret_msg = u"用户编号：" + userno
        if not user_data:
            user_data = dict()
        self.render('user_query_detail.html', ret_msg=ret_msg, data=user_data)

class UserDetailChangeZaunHandler(tornado.web.RequestHandler):
    def post(self):
        userno = self.get_argument('userno')
        user_data = self.application.db.user.find_one({'record.userno': userno})
        ret_msg = str()
        if not user_data or len(user_data) == 0:
           ret_msg = u"没有该用户"
        else:
           ret_msg = u"用户编号：" + userno
        if not user_data:
            user_data = dict()
        self.render('user_query_detail.html', ret_msg=ret_msg, data=user_data)

class UserDataModule(tornado.web.UIModule):
    def render(self, data):
        if data and 'record' in data.keys():
            gold = 0
            zuan = 0
            if 'gold' in data['record'].keys():
                gold = data['record']['gold']
            if 'zuan' in data['record'].keys():
                zuan = data['record']['zuan']
            msg_gold = u"当前金币：" + str(gold)
            msg_zuan = u"当前钻石：" + str(zuan)
            return self.render_string('module/user_data.html', items=data['record'], msg_gold=msg_gold, msg_zuan=msg_zuan)
        else:
            return self.render_string('module/user_data.html', items=dict())


if __name__ == '__main__':
    tornado.options.parse_command_line()
    # app = tornado.web.Application(
    #     handlers=[(r'/', IndexHandler),
    #               (r'/login', LoginHandler),
    #               (r'/userDetail', UserDetailHandler)],
    #     template_path=os.path.join(os.path.dirname(__file__), "templates"),
    #     static_path=os.path.join(os.path.dirname(__file__), "static"),
    #     debug=True
    # )
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
