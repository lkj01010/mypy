import cfg
import tornado.httpclient
import tornado.ioloop

import pymongo
import json
from log import server_log

class Record(object):
    def __init__(self, db_addr, db_port):
        conn = pymongo.MongoClient(db_addr, db_port)
        self.db = conn['dota']
        # for index in self.db.user.list_indexes():
        #     print(index)
        # self.db.user.drop_index('_id') #  drop '_id' is invalid
        self.db.user.create_index('user_id')
        self.db_client = tornado.httpclient.AsyncHTTPClient()
        self.batch = dict()
        pass

    @staticmethod
    def default_record():
        record = {
            # '-1': 0,

            # "0": 50,    # music
            # "1": 50,    # effect
            #
            # "3": -1,    # daily reward
            # "6": 3,     # liuxinghuoyu
            # "7": 15,    # card bag space
            #
            # "kapailan": 3,
            # "chapter": 1,
            # "guanka": 1,
            #
            # "chengshiLv_1": 1,
            # "chengshiLv_2": 1,
            # "chengshiLv_3": 1,
            #
            # "kapai_1": 1,
            # "kapai_2": 1,
            # "kapai_8": 1,
            #
            # "gold": 5000,
            #
            # "11": 1,
            # "12": 1,
            # "13": 1,
            # "14": 1,
            # "15": 1,
            # "16": 1
        }
        return record

    ''' return a record (dict type) '''
    def get_record(self, user_id):
        # find it from record batch first
        if user_id in self.batch:
            return json.JSONDecoder().decode(self.batch[user_id])   # json to dict
        else:
            find_ret = self.db.user.find_one({'user_id': user_id})
            if find_ret:
                del find_ret['_id']
                reply_dict = dict()
                if 'record' in find_ret and type(find_ret['record']) is dict:
                    reply_dict = dict((key.encode('ascii'), value) for key, value in find_ret['record'].items())
                return reply_dict
            else:
                record_doc = dict()
                record_doc['user_id'] = user_id
                record_doc['record'] = Record.default_record()
                self.db.user.insert(record_doc)

                reply_dict = Record.default_record()
                return reply_dict

    def commit_record(self, user_id, record_str):
        # j_info = json.JSONEncoder().encode(record_str)
        # self.db.user.update({'user_id': info['user_id']}, record_str, True)
        self.batch[user_id] = record_str

    def push_records_to_db(self):
        j_record_batch = json.JSONEncoder().encode(self.batch)
        request = tornado.httpclient.HTTPRequest('http://' + cfg.DB_SERVER_ADDR + ':' + str(cfg.DB_SERVER_PORT),
                                                 method='POST', body=j_record_batch)
        self.db_client.fetch(request, callback=Record.push_records_to_db_callback)
        self.batch.clear()

    @staticmethod
    def push_records_to_db_callback(response):
        # print 'syn callback', response.body
        server_log.info('syn callback' + str(response.body))
        pass
