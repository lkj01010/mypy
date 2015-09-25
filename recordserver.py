import cfg
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

define("port", default=12304, help="run on the given port", type=int)
define("db_addr", default="127.0.0.1", help="db addr", type=str)
define("db_port", default=27017, help="db port", type=int)

_SYN_DB_INTERVAL = 5000


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/writeDirtyRecord", WriteDirtyRecordHandler),
            (r"/readRecord", ReadRecordHandler)
        ]
        self.record_mod = record.Record(options.db_addr, options.db_port)

        tornado.web.Application.__init__(self, handlers, debug=False)

    def termly_push_records_to_db(self):
        time_task = tornado.ioloop.PeriodicCallback(self.record_mod.push_records_to_db, _SYN_DB_INTERVAL)
        time_task.start()
        pass


class ReadRecordHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    def get(self):

        try:
            user_id = self.get_argument('user_id')
            user_key = self.get_argument('user_key')
            zoneid = self.get_argument('user_pf')
        except KeyError:
            server_log.warning("except KeyError: Failed to get argument", exc_info=True)

        checker = check_login.LoginChecker()
        checker.check_info(user_id, user_key, zoneid, self._check_ret_callback)

    def _check_ret_callback(self, is_valid):
        reply_dict = dict()
        reply_dict['code'] = 0
        reply_dict['record'] = dict()

        if is_valid:
            reply_dict['code'] = 1
            user_uid = self.get_argument('user_id') + '_' + self.get_argument('user_pf')
            reply_dict['record'] = self.application.record_mod.get_record(user_uid)

            reply = str(self.get_argument('callback')) + '(' + json.dumps(reply_dict) + ')'
            self.write(reply)      # this function will add '//' to words, overwrite reply !!!
            server_log.info('read: ' + reply)
        else:
            '''wrong user_id or user_key'''
            reply_dict['code'] = 1
            reply = str(self.get_argument('callback')) + '(' + "{'code':0, 'msg':'invid userid'}" + ')'
            self.write(reply)

        self.finish()

class WriteDirtyRecordHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        try:
            user_id = self.get_argument('user_id')
            user_key = self.get_argument('user_key')
            zoneid = self.get_argument('user_pf')
        except KeyError:
            server_log.warning("Failed to get argument", exc_info=True)

        checker = check_login.LoginChecker()
        checker.check_info(user_id, user_key, zoneid, self._check_ret_callback)

    def _check_ret_callback(self, is_valid):
        if is_valid:
            user_pf = self.get_argument('user_pf')
            user_uid = self.get_argument('user_id') + '_' + user_pf
            dirty_id = self.get_argument('dirty_id')
            # commit dirty record
            self.application.record_mod.commit_dirty_record(user_uid, self.get_argument('dirty_record'))
            replay = self.get_argument('callback') + '({' + \
                "'dirty_id':" + dirty_id + ',' + \
                "'msg': 'push ok'" + \
                '})'
        else:
            '''wrong user_id or user_key'''
            replay = str(self.get_argument('callback') + '(' + "{'new account': 'invalid account'}" + ')')
        self.write(replay)
        self.finish()

    def _test_get(self):
        coll = self.application.db.user
        print 'coll :', coll

        self.set_status(200)

        # result = None

        coll.ensure_index('index')
        for i in range(100):
            result = coll.insert_one({'index': i, 'index2': i, 'index3': i, 'index4': i, 'index5': "abcdefgggggg"})
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

    # test this !!!
    # http://127.0.0.1:12304/writeRecord?user_id=userid_ooxxooxx&user_key=key0123&record={}&callback=jQuery17204590415961574763_1441798647346&_=1441798742602
