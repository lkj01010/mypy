# -*- coding: UTF-8 -*-
import cfg
import tornado.httpclient
import tornado.ioloop

import pymongo
import json
from log import server_log
import time
import random
import copy

class Record(object):
    def __init__(self, db_addr, db_port):
        conn = pymongo.MongoClient(db_addr, db_port)

        self.db = conn['dota']
        # self.db.user.drop_index('_id') #  drop '_id' is invalid
        self.db.user.create_index('user_uid')
        self.db_client = tornado.httpclient.AsyncHTTPClient()
        self.is_pushing = False
        self.batch = dict()
        self.batch_on_pushing = dict()  # cache batch using until pushing data to db complete
        # self.cache = dict()
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
            "gold": 5000,
            "zuan": 0,
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
    def get_record_old(self, user_uid):
        # find it from record batch first
        server_log.info('get record. user_uid=' + user_uid)

        if not self.is_pushing and user_uid in self.batch:
            # return json.JSONDecoder().decode(self.batch[user_uid])   # json to dict
            server_log.info('batch : ' + str(self.batch))
            return self.batch[user_uid]   # json to dict

        elif self.is_pushing and user_uid in self.batch_on_pushing:
            # return json.JSONDecoder().decode(self.batch_on_pushing[user_uid])
            server_log.info('batch_on_pushing : ' + str(self.batch_on_pushing))
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
                server_log.info('not find record of user_uid=' + user_uid + ', make default record !!!')
                record_doc = dict()
                record_doc['user_uid'] = user_uid
                record_doc['record'] = Record.default_record()
                self.db.user.insert(record_doc)

                reply_dict = Record.default_record()
                return reply_dict

    '''-------------------------------------'''
    def _make_userno(self):
        count = self.db.user.count()
        count = (10000 + count) * 100 + random.randint(0, 99)
        return str(count)

    def get_record(self, user_uid):
        # server_log.info('get record. user_uid=' + user_uid)
        # if user_uid not in self.cache:
        #     server_log.info('not in cache')

            find_ret = self.db.user.find_one({'user_uid': user_uid})

            if find_ret:
                server_log.info('db find')
                del find_ret['_id']
                reply_dict = dict()
                if 'record' in find_ret and type(find_ret['record']) is dict:
                    # reply_dict = dict((key.encode('ascii'), value) for key, value in find_ret['record'].items())
                    reply_dict = find_ret['record']

                """attach unpushed record item to Record(old) from db"""
                if user_uid in self.batch_on_pushing:
                    server_log.warning('attach record_on_pushing: ' + user_uid +
                                    ', record: ' + str(self.batch_on_pushing[user_uid]))
                    reply_dict.update(self.batch_on_pushing[user_uid])
                if user_uid in self.batch:
                    server_log.info('attach record_batch: ' + user_uid +
                                    ', record: ' + str(self.batch[user_uid]))
                    reply_dict.update(self.batch[user_uid])

                """add unique number id"""
                if 'userno' not in reply_dict:
                    reply_dict['userno'] = self._make_userno()
            else:
                server_log.info('not find record of user_uid=' + user_uid + ', make default record !!!')
                record_doc = dict()
                record_doc['user_uid'] = user_uid
                record_doc['record'] = Record.default_record()
                record_doc['record']['userno'] = self._make_userno()
                self.db.user.insert(record_doc)
                reply_dict = record_doc['record']

            return reply_dict
        # else:
        #     server_log.info('in cache, record=' + str(self.cache[user_uid]))
        #     return self.cache[user_uid]

    def commit_dirty_record(self, user_uid, dirty_record_str):
        dirty_record_dict = json.JSONDecoder().decode(dirty_record_str)

        if user_uid not in self.batch:
            server_log.error('new dict')
            self.batch[user_uid] = dict()

        # server_log.error('user_uid: ' + user_uid + ', dirty_str: ' + dirty_record_str)
        # server_log.error('batch before attach: ' + str(self.batch))
        self.batch[user_uid].update(dirty_record_dict)
        # server_log.error('batch after attach: ' + str(self.batch))

        if user_uid in self.batch_on_pushing:
            self.batch_on_pushing[user_uid].update(dirty_record_dict)

    def push_records_to_db(self):
        j_record_batch = json.JSONEncoder().encode(self.batch)
        # server_log.error('push batch: ' + j_record_batch)
        request = tornado.httpclient.HTTPRequest(cfg.DB_SERVER, method='POST', body=j_record_batch)
        self.db_client.fetch(request, callback=self.push_records_to_db_callback)

        self.batch_on_pushing = copy.deepcopy(self.batch)
        self.batch.clear()

    def push_records_to_db_callback(self, response):
        if response.body:
            self.batch_on_pushing.clear()
            # server_log.info('syn response: ' + str(response.body))
        else:
            # TODO : error handle: 备份没有提交的 on_push 到现有的 batch 上
            self.batch_on_pushing.update(self.batch)
            self.batch = copy.deepcopy(self.batch_on_pushing)
            self.batch_on_pushing.clear()
            server_log.info('push error !!!!!!!!!!!!! syn response: ' + str(response.body))



    '''-------------------------------------'''
    # def commit_record(self, user_uid, record_str):
    #     # j_info = json.JSONEncoder().encode(record_str)
    #     # self.db.user.update({'user_id': info['user_id']}, record_str, True)
    #     if not self.is_pushing:
    #         self.batch[user_uid] = record_str
    #     else:
    #         self.batch_on_pushing[user_uid] = record_str

    # def commit_dirty_record_old(self, user_uid, dirty_record_str):
    #     dirty_record_dict = json.JSONDecoder().decode(dirty_record_str)
    #     if not self.is_pushing:
    #         if not self.batch.has_key(user_uid):
    #             self.batch[user_uid] = dict()
    #         self.batch[user_uid].update(dirty_record_dict)
    #     else:
    #         if not self.batch_on_pushing.has_key(user_uid):
    #             self.batch_on_pushing[user_uid] = dict()
    #         self.batch_on_pushing[user_uid].update(dirty_record_dict)
    #
    # def push_records_to_db_old(self):
    #     j_record_batch = json.JSONEncoder().encode(self.batch)
    #     request = tornado.httpclient.HTTPRequest(cfg.DB_SERVER, method='POST', body=j_record_batch)
    #     self.db_client.fetch(request, callback=self.push_records_to_db_callback_old)
    #     self.is_pushing = True
    #
    # def push_records_to_db_callback_old(self, response):
    #     if response.body:
    #         # print 'syn callback', response.body
    #         # manage batch for new turn
    #         self.batch = {}
    #         self.batch = copy.deepcopy(self.batch_on_pushing)
    #         # self.batch_on_pushing.clear()   # lkj note: clear not clear the key !!!
    #         self.batch_on_pushing = {}
    #         self.is_pushing = False
    #     else:
    #         pass
    #     server_log.info('syn response: ' + str(response.body))

    '''------------------------------------'''
    def push_record_to_db(self, user_uid, record_str):
        """push single record to db"""
        record = dict()
        record[user_uid] = record_str
        j_record_batch = json.JSONEncoder().encode(record)
        request = tornado.httpclient.HTTPRequest(cfg.DB_SERVER, method='POST', body=j_record_batch)
        self.db_client.fetch(request, callback=self.push_record_to_db_callback)

    def push_record_to_db_callback(self, response):
        if response.body:
            pass
        else:
            # TODO : error handle
            pass
        server_log.info('syn immediately response: ' + str(response.body))


