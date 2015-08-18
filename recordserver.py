import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import pymongo

from tornado.options import define, options
define("port", default=8010, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", WriteRecordHandler),
            (r"/dota/writeRecord", WriteRecordHandler),
            (r"/dota/readRecord", ReadRecordHandler)
            ]
        conn = pymongo.MongoClient("192.168.1.250", 27017)
        self.db = conn["dota"]

        tornado.web.Application.__init__(self, handlers, debug=True)

class ReadRecordHandler(tornado.web.RequestHandler):
    def get(self):
        coll = self.application.db.user
        print coll
        user = coll.find_one({"name": "lkj"})
        print user
        if user:
            del user["_id"]
            self.write(user)
        else:
            self.set_status(404)
            self.write({"error": "user not found"})

class WriteRecordHandler(tornado.web.RequestHandler):
    def get(self):
         coll = self.application.db.user

         self.set_status(200)
         for i in range(500):
            result = coll.insert_one({'index':i})
            print str(result)
            print coll.find_one({''})
            self.write(str(result))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()