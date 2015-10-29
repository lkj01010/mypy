# -*- coding: UTF-8 -*-
import cfg
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json
import pymongo
import time

from log import server_log

from tornado.options import define, options

define("port", default=12305, help="run on the given port", type=int)
define("db_addr", default="127.0.0.1", help="db addr", type=str)
define("db_port", default=27017, help="db port", type=int)


class Application(tornado.web.Application):
    """this server directly save actions log of users to db"""

    def __init__(self):
        handlers = [
            (r"/writeStat", WriteStatToDBHandler),
            (r"/querySrvState", QuerySrvStateHandler),
            (r"/cmd", CommandHandler),
        ]
        server_log.info('stat server start on db[' + options.db_addr + ':' + str(options.db_port) + ']')

        conn = pymongo.MongoClient(options.db_addr, options.db_port)
        self.db = conn['dota']
        self.db.stat.create_index('user_uid')
        server_log.info('connect server OK')

        self.client = tornado.httpclient.AsyncHTTPClient()

        """server state"""
        self.server_running = True
        self.server_state_msg = ""

        tornado.web.Application.__init__(self, handlers, debug=True)


class WriteStatToDBHandler(tornado.web.RequestHandler):

    _MAX_ACTION_EACH_ID = 1000          # count of actions save to db each account

    def get(self):
        """as it is not a strictly important part, need not to check user certification"""
        user_uid = self.get_argument('openid') + '_' + self.get_argument('user_pf')
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        push_str = self.get_argument('stat')

        push_dict = json.JSONDecoder().decode(push_str)
        push_dict['modify_time'] = modify_time

        self.application.db.stat.update({'user_uid': user_uid},
                                        {
                                            '$push': {
                                                'actions': {
                                                    '$each': [push_dict],
                                                    '$slice': -WriteStatToDBHandler._MAX_ACTION_EACH_ID
                                                },
                                            },
                                            '$set': {
                                                'last_modify': modify_time
                                            }}, True, False)
        server_log.info(str(push_dict))
        self.write(str(self.get_argument('callback') + '(' + "{'ok': 1}" + ')'))

class QuerySrvStateHandler(tornado.web.RequestHandler):
    def get(self):
        callback = self.get_argument('callback')
        if self.application.server_running:
            reply = "{'state':1,'msg':'" + "" + "'}"
        else:
            reply = "{'state':0,'msg':'" + self.application.server_state_msg + "'}"
        reply = callback.encode('utf8') + '(' + reply + ')'
        self.write(reply)

class CommandHandler(tornado.web.RequestHandler):

    def get(self):
        """
        type:0  停机维护
            msg：
        """
        print self.request.remote_ip
        if self.request.remote_ip == '127.0.0.1':
            command = self.get_argument('cmd')
            cmd_dict = json.JSONDecoder().decode(command)
            server_log.warn( 'cmd is: ' + str(cmd_dict))
            try:
                if cmd_dict["type"] == 0:
                    self.application.server_state_msg = cmd_dict["msg"]
                    self.application.server_running = False
                elif cmd_dict["type"] == 1:
                    self.application.server_state_msg = ""
                    self.application.server_running = True

                """存档服务器"""
                request = tornado.httpclient.HTTPRequest(cfg.RECORD_SERVER + '/cmd', method='POST', body=command)
                self.application.client.fetch(request, callback=CommandHandler.cmd_callback)
                """openapi服务器"""
                request = tornado.httpclient.HTTPRequest(cfg.TENCENT_ACCOUNT_SERVER + '/cmd', method='POST',
                                                         body=command)
                self.application.client.fetch(request, callback=CommandHandler.cmd_callback)

                self.write("hello")
                # self.send_error()
            except KeyError:
                pass
        pass

    @staticmethod
    def cmd_callback(response):
        print 'cmd callback msg: ', response.body

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
