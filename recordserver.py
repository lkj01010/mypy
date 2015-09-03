import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json

import pdb
import copy

from log import server_log
import check_login
import record


from tornado.options import define, options
define("port", default=8010, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", WriteRecordHandler),
            (r"/writeRecord", WriteRecordHandler),
            (r"/readRecord", ReadRecordHandler)
            ]
        self.check_mod = check_login.CheckLogin()
        self.record_mod = record.Record()
        # conn = pymongo.MongoClient("192.168.1.250", 27017)
        # self.db = conn["dota"]

        tornado.web.Application.__init__(self, handlers, debug=False)


class ReadRecordHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        reply_dict = dict()
        reply_dict['code'] = 0
        reply_dict['msg'] = ''
        reply_dict['record'] = dict()

        try:
            user_id = self.get_argument('userid')
            user_key = self.get_argument('userkey')
            cb_name = self.get_argument('callback')
        except KeyError:
            server_log.warning("Failed to get argument", exc_info=True)

        if self.application.check_mod.check_info(user_id, user_key):
            reply_dict['code'] = 1
            reply_dict['record'] = self.application.record_mod.get_record(user_id)

            replay = str(cb_name) + '(' + json.dumps(reply_dict) + ')'
            self.write(replay)
            server_log.info(replay)

            # if user:
            #     del user["_id"]
            #     self.write(user)
            # else:
            #     self.set_status(404)
            #     self.write({"error": "user not found"})
        else:
            '''wrong user_id or user_key'''
            return


class WriteRecordHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self, *args, **kwargs):
        replay_dict = dict()
        replay_dict['is_ok'] = 0
        replay_dict['msg'] = ''

        user_id = self.request.query_arguments['userid']
        user_key = self.request.query_arguments['userkey']

        if self.application.check_mod.check_info(user_id, user_key):
            self.application.reocord_mod.commit_record_item(user_id, {'test_key': 'test_key'})

    def _test_get(self):
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