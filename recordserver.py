import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json

import pymongo

import pdb

from tornado.options import define, options
define("port", default=8010, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", WriteRecordHandler),
            (r"/writeRecord", WriteRecordHandler),
            (r"/readRecord", ReadRecordHandler)
            ]
        conn = pymongo.MongoClient("10.211.55.6", 27017)
        self.db = conn["dota"]

        tornado.web.Application.__init__(self, handlers, debug=True)


class ReadRecordHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        coll = self.application.db.user
        print 'coll :', coll
        user = coll.find_one({"name": "lkj"})
        print 'user :', user
        if user:
            del user["_id"]
            self.write(user)
        else:
            self.set_status(404)
            self.write({"error": "user not found"})


class WriteRecordHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        coll = self.application.db.user
        print 'coll :', coll

        self.set_status(200)

        lenth = 0
        # result = None

        coll.ensure_index('index')
        for i in range(100):
            result = coll.insert_one({'index':i, 'index2':i, 'index3':i, 'index4':i, 'index5':"abcdefgggggg"})
            # print str(result)
            # print coll.find_one({'index':i})

            # doc = coll.find_one({'index':i})
            # print 'before dumps:',doc
            # del doc['_id']

            # doc = {'index':1, 'haha':'...'}
            # appendstr = json.dumps(doc) + "appendstr"*1000
            # lenth += len(appendstr)
            # self.write(appendstr)
            # print "lenth is", lenth
        self.write('1')
        # print 'result is' , str(result)
        print "lenth is", lenth
        print coll.count()

if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

# find_one 10000 times in 5w with index uses 2522ms
# insert_one 10000 times in 5w(to 6w) with index uses 2662ms