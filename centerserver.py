# -*- coding: UTF-8 -*-

import cfg
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web
import json

import pymongo
import uuid

from log import server_log

from tornado.options import define, options

define("rt", default='', help="reomote type", type=str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/client", ClientReqHandler),
            (r"/acsp/paycb", AcspPayCbHandler),
        ]
        conn = pymongo.MongoClient(cfg.srvcfg['ip_mongodb'], cfg.srvcfg['port_mongodb'])
        self.db = conn[cfg.srvcfg['comdbname_mongodb']]
        self.db.user.create_index('user_uid')
        server_log.info('center server start on port: ' + str(cfg.srvcfg['port_center']))

        tornado.web.Application.__init__(self, handlers, debug=False)

class ClientReqHandler(tornado.web.RequestHandler):
    def get(self):
        reply_dict = dict()
        # user_uid = cfg.format_user_uid(self.get_argument('user_id'), self.get_argument('user_pf'))
        order_id = uuid.uuid1()
        reply_dict['order_id'] = order_id
        reply = str(self.get_argument('callback')) + '(' + json.dumps(reply_dict) + ')'
        server_log.info('acsp gen order_id: ' + order_id)
        self.write(reply)
        pass

class AcspPayCbHandler(tornado.web.RequestHandler):
    def get(self):
        self.send_error()

    def post(self, *args, **kwargs):
        body = self.request.body
        print body
        self.send_error()
        # server_log.warn('receive cmd :\n' + command_str)
        # command_dict = json.JSONDecoder().decode(command_str)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    cfg.setup_srvcfg(options.rt)
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(cfg.srvcfg['port_center'])
    tornado.ioloop.IOLoop.instance().start()


    # find_one 10000 times in 5w with index uses 2522ms
    # insert_one 10000 times in 5w(to 6w) with index uses 2662ms

    # test this !!!
    # http://127.0.0.1:12304/writeRecord?user_id=userid_ooxxooxx&user_key=key0123&record={}&callback=jQuery17204590415961574763_1441798647346&_=1441798742602


