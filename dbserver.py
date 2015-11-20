# -*- coding: UTF-8 -*-
import cfg
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json
import pymongo
from pymongo.collection import Collection
import datetime
import pdb
import copy
import time

from log import server_log

from tornado.options import define, options

define("port", default=12310, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", WriteRecordToDBHandler),
            (r"/billinfo", WriteBillToDBHandler),
            (r"/recordBatch", WriteRecordBatchHandler),
            (r"/srvStat", WriteSrvStatHandler),
            (r"/db", WriteDBHandler),
        ]

        server_log.info('db server start on db[' + cfg.DB_ADDR + ':' + str(cfg.DB_PORT) + ']')

        conn = pymongo.MongoClient(cfg.DB_ADDR, cfg.DB_PORT)
        self.db = conn['dota']
        self.db.user.create_index('user_uid')

        self.db.bill.create_index('billno')
        self.db.bill.create_index('create_time')

        tornado.web.Application.__init__(self, handlers, debug=True)


class WriteRecordToDBHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

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


class WriteRecordBatchHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        batch_str = self.request.body
        batch_dict = json.JSONDecoder().decode(batch_str)
        for user_id, record_dict in batch_dict.items():
            doc = dict()
            doc['user_uid'] = user_id
            doc['modify_time'] = datetime.datetime.now()
            doc['record'] = record_dict
            server_log.info('db write this: user_uid:' + user_id + '\ndoc: ' + str(doc))
            result = self.application.db.user.replace_one({'user_uid': user_id}, doc, True)
            print str(result)
        self.write("{'ok': 1, 'msg': 'push record'}")

class WriteBillToDBHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self, *args, **kwargs):
        bill_str = self.request.body
        bill_dict = json.JSONDecoder().decode(bill_str)
        bill_dict['create_time'] = datetime.datetime.now()

        self.application.db.bill.insert_one(bill_dict)
        server_log.info('db write bill: ' + str(bill_dict))

        self.write("{'ok': 1, 'msg': 'push bill'}")

class WriteSrvStatHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        stat_str = self.request.body
        server_log.info('stat info: ' + stat_str)
        stat_dict = json.JSONDecoder().decode(stat_str)
        stat_dict['value']['time'] = datetime.datetime.now()

        db = self.application.db
        """stat_dict['collection'] should be a list string"""
        name = ''
        for v in stat_dict['collection']:
            name += v + '.'
        name = name[:-1]
        c = Collection(db, name)
        if stat_dict['key']:
            c.update(stat_dict['key'], stat_dict['value'], True, False)
        else:
            c.insert_one(stat_dict['value'])

class WriteDBHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        req_str = self.request.body
        server_log.info('request info: ' + req_str)
        req_dict = json.JSONDecoder().decode(req_str)

        db = self.application.db

        c = Collection(db, req_dict['collection'])
        if 'batch' in req_dict and type(req_dict['batch']) == list:
            for v in req_dict['batch']:
                if v['filter']:
                    if v['modifier'] == 'set':
                        c.update_one(v['filter'],
                                     {'$set':
                                        {v['update']['key']: v['update']['value']}
                                      }, True)
                    elif v['modifier'] == 'delete':
                        c.delete_one(v['filter'])
                else:
                    c.insert_one(v['doc'])
        self.write("{'ok': 1, 'msg': 'push to '" + req_dict['collection'] + "}")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
