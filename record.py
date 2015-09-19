import cfg
import tornado.httpclient
import tornado.ioloop

import pymongo
import json
from log import server_log
import copy

class Record(object):
    def __init__(self, db_addr, db_port):
        conn = pymongo.MongoClient(db_addr, db_port)
        self.db = conn['dota']
        # for index in self.db.user.list_indexes():
        #     print(index)
        # self.db.user.drop_index('_id') #  drop '_id' is invalid
        self.db.user.create_index('user_uid')
        self.db_client = tornado.httpclient.AsyncHTTPClient()
        self.is_pushing = False
        self.batch = dict()
        self.batch_on_pushing = dict()  # cache batch using until pushing data to db complete
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
    def get_record(self, user_uid):
        # find it from record batch first
        if not self.is_pushing and user_uid in self.batch:
            # return json.JSONDecoder().decode(self.batch[user_uid])   # json to dict
            return self.batch[user_uid]   # json to dict

        elif self.is_pushing and user_uid in self.batch_on_pushing:
            # return json.JSONDecoder().decode(self.batch_on_pushing[user_uid])
            return self.batch_on_pushing[user_uid]

        else:
            find_ret = self.db.user.find_one({'user_uid': user_uid})
            if find_ret:
                del find_ret['_id']
                reply_dict = dict()
                if 'record' in find_ret and type(find_ret['record']) is dict:
                    # reply_dict = dict((key.encode('ascii'), value) for key, value in find_ret['record'].items())
                    reply_dict = find_ret['record']
                return reply_dict
            else:
                record_doc = dict()
                record_doc['user_uid'] = user_uid
                record_doc['record'] = Record.default_record()
                self.db.user.insert(record_doc)

                reply_dict = Record.default_record()
                return reply_dict

    def commit_record(self, user_uid, record_str):
        # j_info = json.JSONEncoder().encode(record_str)
        # self.db.user.update({'user_id': info['user_id']}, record_str, True)
        if not self.is_pushing:
            self.batch[user_uid] = record_str
        else:
            self.batch_on_pushing[user_uid] = record_str

    def commit_dirty_record(self, user_uid, dirty_record_str):
        dirty_record_dict = json.JSONDecoder().decode(dirty_record_str)
        if not self.is_pushing:
            self.batch[user_uid].update(dirty_record_dict)
        else:
            self.batch_on_pushing[user_uid].update(dirty_record_dict)
        pass

    def push_records_to_db(self):
        j_record_batch = json.JSONEncoder().encode(self.batch)
        request = tornado.httpclient.HTTPRequest('http://' + cfg.DB_SERVER_ADDR + ':' + str(cfg.DB_SERVER_PORT),
                                                 method='POST', body=j_record_batch)
        self.db_client.fetch(request, callback=self.push_records_to_db_callback)
        self.is_pushing = True

    def push_records_to_db_callback(self, response):
        # print 'syn callback', response.body
        server_log.info('syn callback' + str(response.body))
        # manage batch for new turn
        self.batch.clear()
        self.batch = copy.deepcopy(self.batch_on_pushing)
        self.batch_on_pushing.clear()
        self.is_pushing = False
        pass
