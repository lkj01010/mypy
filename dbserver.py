import cfg
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json
import pymongo
import pdb
import copy

from log import server_log


from tornado.options import define, options
define("port", default=8020, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", WriteDocToDBHandler)
            ]

        conn = pymongo.MongoClient(cfg.DB_ADDR, cfg.DB_PORT)
        self.db = conn['dota']
        self.db.user.create_index('user_id')

        tornado.web.Application.__init__(self, handlers, debug=True)

class WriteDocToDBHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        batch_str = self.request.body
        print 'will write this: ', str(batch_str)
        batch_dict = json.JSONDecoder().decode(batch_str)
        doc_dict = dict()
        for user_id, record_str in batch_dict.items():
            record_dict = json.JSONDecoder().decode(record_str)
            doc_dict['user_id'] = user_id
            doc_dict['record'] = record_dict
            self.application.db.user.update({'user_id': user_id}, doc_dict, True)
        self.write("{'ok': 1}")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(cfg.DB_SERVER_PORT)
    tornado.ioloop.IOLoop.instance().start()
