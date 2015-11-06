# -*- coding: UTF-8 -*-
import cfg
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json
import pymongo
import pdb
import copy
import time

from log import server_log

from tornado.options import define, options

define("port", default=12306, help="run on the given port", type=int)
define("db_addr", default="127.0.0.1", help="db addr", type=str)
define("db_port", default=27017, help="db port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/ranklist", GetRankListHandler),
            (r"/billinfo", WriteBillToDBHandler)
        ]

        server_log.info('db server start on db[' + options.db_addr + ':' + str(options.db_port) + ']')

        conn = pymongo.MongoClient(options.db_addr, options.db_port)
        self.db = conn['dota']
        self.db.jjc.create_index('honour')
        self._predeploy_users()

        tornado.web.Application.__init__(self, handlers, debug=True)

    def _predeploy_users(self):
        pass


class GetRankListHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        if self.application.running:
            try:
                user_id = self.get_argument('user_id')
                user_key = self.get_argument('user_key')
                zoneid = self.get_argument('user_pf')
            except KeyError:
                server_log.warning("Failed to get argument", exc_info=True)

            checker = check_login.LoginChecker()
            checker.check_info(user_id, user_key, zoneid, self._check_ret_callback)
        else:
            self.send_error()

    def post(self, *args, **kwargs):
        batch_str = self.request.body
        # print 'will write this: ', str(batch_str)
        batch_dict = json.JSONDecoder().decode(batch_str)
        # modify_time = time.ctime()
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for user_id, record_dict in batch_dict.items():
            """ split the dict, and update data partly use '$set' to db"""
            set_dict = dict()
            set_dict['user_uid'] = user_id
            set_string = ''
            for k, v in record_dict.items():
                set_string += "'record.%s':'%s'," % (k, v)
                set_dict['record.%s' % k] = v
            set_dict['modify_time'] = modify_time
            self.application.db.user.update({'user_uid': user_id}, {'$set': set_dict}, True, False)
            server_log.info('db write this: user_uid:' + user_id + ' doc: ' + str(set_dict))

        self.write("{'ok': 1, 'msg': 'push record'}")


class WriteBillToDBHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        bill_str = self.request.body
        bill_dict = json.JSONDecoder().decode(bill_str)

        self.application.db.bill.insert_one(bill_dict)
        server_log.info('db write bill: ' + str(bill_dict))

        self.write("{'ok': 1, 'msg': 'push bill'}")


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
