import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json

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

        tornado.web.Application.__init__(self, handlers, debug=True)

class WriteDocToDBHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        body = self.request.body
        print 'will write this: ', str(body)
        self.write("{'ok': 1}")
        pass

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
