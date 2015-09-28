# -*- coding: UTF-8 -*-
import cfg
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
            (r"/", WriteStatToDBHandler)
        ]
        server_log.info('stat server start on db[' + options.db_addr + ':' + str(options.db_port) + ']')

        conn = pymongo.MongoClient(options.db_addr, options.db_port)
        self.db = conn['dota']
        self.db.stat.create_index('user_uid')

        tornado.web.Application.__init__(self, handlers, debug=True)


class WriteStatToDBHandler(tornado.web.RequestHandler):

    _MAX_ACTION_EACH_ID = 3          # count of actions save to db each account

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


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
