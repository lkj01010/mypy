import tornado.httpserver
import tornado.httpclient
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

_SYN_DB_INTERVAL = 1000

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", WriteRecordHandler),
            (r"/writeRecord", WriteRecordHandler),
            (r"/readRecord", ReadRecordHandler)
            ]
        self.check_mod = check_login.CheckLogin()
        self.record_mod = record.Record()
        self.db_client = tornado.httpclient.AsyncHTTPClient()

        tornado.web.Application.__init__(self, handlers, debug=False)

    def termly_push_records_to_db(self):
        time_task = tornado.ioloop.PeriodicCallback(self.push_records_to_db, _SYN_DB_INTERVAL)
        time_task.start()
        pass

    def push_records_to_db(self):
        request = tornado.httpclient.HTTPRequest('http://127.0.0.1:8020', method='POST', body="{'push': 1}")
        self.db_client.fetch(request, callback=Application.push_records_to_db_callback)

    @staticmethod
    def push_records_to_db_callback(response):
        print 'syn callback', response.body
        pass

class ReadRecordHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        reply_dict = dict()
        reply_dict['code'] = 0
        # reply_dict['type'] = 'read'
        reply_dict['record'] = dict()

        try:
            user_id = self.get_argument('user_id')
            user_key = self.get_argument('user_key')
            cb_name = self.get_argument('callback')
        except KeyError:
            server_log.warning("Failed to get argument", exc_info=True)

        if self.application.check_mod.check_info(user_id, user_key):
            reply_dict['code'] = 1
            reply_dict['record'] = self.application.record_mod.get_record(user_id)

            replay = str(cb_name) + '(' + json.dumps(reply_dict) + ')'
            self.write(replay)
            server_log.info('read: ' + replay)

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
        save_dict = dict()
        save_dict['record'] = dict()

        try:
            user_id = self.get_argument('user_id')
            user_key = self.get_argument('user_key')
            # cb_name = self.get_argument('callback')
            record_str = self.get_argument('record')
        except KeyError:
            server_log.warning("Failed to get argument", exc_info=True)

        if self.application.check_mod.check_info(user_id, user_key):
            save_dict['user_id'] = user_id
            save_dict['record'] = json.JSONDecoder().decode(record_str)

            # replay = str(cb_name) + '(' + "{'code': 1}" + ')'
            # self.write(replay)
            self.application.record_mod.commit_record(save_dict)
            # server_log.info('save: ' + replay)
        else:
            '''wrong user_id or user_key'''
            return

        # if self.application.check_mod.check_info(user_id, user_key):
        #     self.application.reocord_mod.commit_record_item(user_id, {'test_key': 'test_key'})

    def _test_get(self):
        coll = self.application.db.user
        print 'coll :', coll

        self.set_status(200)

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
    app = Application()
    app.termly_push_records_to_db()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


# find_one 10000 times in 5w with index uses 2522ms
# insert_one 10000 times in 5w(to 6w) with index uses 2662ms