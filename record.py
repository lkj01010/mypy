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
import datetime


class _DataHolder(object):
    def __init__(self, data):
        self.data = data
        self.touch = 0
        self.push = 0
        self.active = False


class Record(object):

    _SYN_DB_INTERVAL = 10000    # 5*60*1000
    _CLEAN_INACTIVE_RECORDS_INTERVAL = 60000    # 6*60*60*1000
    _STAT_INTERVAL = 10000  # 10*60*1000

    def __init__(self, db_addr, db_port):
        conn = pymongo.MongoClient(db_addr, db_port)

        self.db = conn['dota']
        # self.db.user.drop_index('_id') #  drop '_id' is invalid
        self.db.user.create_index('user_uid')
        self.db_client = tornado.httpclient.AsyncHTTPClient()
        """record save in"""
        self.cache = dict()

        time_task = tornado.ioloop.PeriodicCallback(self.push_dirty_records_to_db, Record._SYN_DB_INTERVAL)
        time_task.start()

        time_task2 = tornado.ioloop.PeriodicCallback(self._clean_inactive_records,
                                                     Record._CLEAN_INACTIVE_RECORDS_INTERVAL)
        time_task2.start()

        self._stat_write_count = 0
        self._stat_read_count = 0
        time_task3 = tornado.ioloop.PeriodicCallback(self._stat_active_user, Record._STAT_INTERVAL)
        time_task3.start()

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

    def get_record(self, user_uid):
        """return a record (dict type)"""
        self._stat_read_count += 1
        if user_uid in self.cache:
            reply_dict = self.cache[user_uid].data
            server_log.warning("cache size=%d, in cache: user_uid=%s" % (len(self.cache), user_uid))
            return reply_dict
        else:
            find_ret = self.db.user.find_one({'user_uid': user_uid})
            if find_ret:
                del find_ret['_id']
                del find_ret['create_time']
                # reply_dict = dict()
                # if 'record' in find_ret and type(find_ret['record']) is dict:
                    # reply_dict = dict((key.encode('ascii'), value) for key, value in find_ret['record'].items())
                reply_dict = find_ret['record']
                server_log.warning('cache size=%d,find from db user_uid=%s' % (len(self.cache), user_uid))
            else:
                reply_dict = dict()
                reply_dict['user_uid'] = user_uid
                reply_dict['record'] = Record.default_record()
                reply_dict['record']['userno'] = self._make_userno()
                reply_dict['create_time'] = datetime.datetime.now()
                self.db.user.insert(reply_dict)     # this oper will add '_id' item !!!
                server_log.warning('cache size=%d,not found, new user_uid=%s' % (len(self.cache), user_uid))
                reply_dict = reply_dict['record']
            self.cache[user_uid] = _DataHolder(reply_dict)
            return reply_dict

    def commit_record(self, user_uid, dirty_record_str):
        self._stat_write_count += 1
        dirty_record_dict = json.JSONDecoder().decode(dirty_record_str)
        if user_uid in self.cache:  # normal
            self.cache[user_uid].data.update(dirty_record_dict)
            self.cache[user_uid].touch += 1
        else:   # abnormal! error!
            """warning: nearly most time, user should in cache, but not!"""
            server_log.warning('warning: nearly most time, user should in cache, but not! user_uid=' + user_uid)
            find_ret = self.db.user.find_one({'user_uid': user_uid})
            if find_ret:
                del find_ret['_id']
                del find_ret['create_time']
                reply_dict = find_ret['record']
                reply_dict.update(dirty_record_dict)
                self.cache[user_uid] = _DataHolder(reply_dict)
                self.cache[user_uid].touch += 1
            else:
                server_log.error('error: commit record, but user not found!!!')

    def push_dirty_records_to_db(self):
        batch = dict()
        for k, v in self.cache.items():
            if v.touch > 0:
                batch[k] = v.data
                v.touch = 0
                v.active = True
                """ after 50 cleanup circle,v will release from cache """
                if v.push < 2:  # test
                    v.push += 1

        # [[ test for log
        logstr = str()
        for k in self.cache:
            logstr += '\nuser_uid=' + k + ', touch=' + str(self.cache[k].touch) + ', push=' + str(self.cache[k].push)
        server_log.info('[push dirty]' + logstr)
        # ]]

        j_record_batch = json.JSONEncoder().encode(batch)
        request = tornado.httpclient.HTTPRequest(cfg.DB_SERVER + '/recordBatch', method='POST', body=j_record_batch)
        self.db_client.fetch(request, callback=self.push_dirty_records_to_db_callback)
        pass

    def push_dirty_records_to_db_callback(self, response):
        if response.body:
            pass
        else:
            server_log.error('push error !!!!!!!!!!!!! syn response: ' + str(response.body))

    def _clean_inactive_records(self):
        for k, v in self.cache.items():
            if v.push <= 0:
                del self.cache[k]
            else:
                self.cache[k].push -= 1

        # [[ test for log
        logstr = str()
        for k in self.cache:
            logstr += '\nuser_uid=' + k + ', touch=' + str(self.cache[k].touch) + ', push=' + str(self.cache[k].push)
        server_log.info('[push inactive]' + logstr)
        # ]]

    def _make_userno(self):
        count = self.db.user.count()
        count = (10000 + count) * 100 + random.randint(0, 99)
        return str(count)

    def _stat_active_user(self):
        active = 0
        for k, v in self.cache.items():
            if v.active:
                active += 1
            v.active = False       # reset

        collection_path = list()
        collection_path.append('srvstat')
        collection_path.append('rt')    # real time

        info = dict()
        info['read'] = self._stat_read_count
        info['write'] = self._stat_write_count
        info['active'] = active

        stat_dict = dict()
        stat_dict['collection'] = collection_path
        stat_dict['key'] = {}
        stat_dict['value'] = info

        j_stat = json.JSONEncoder().encode(stat_dict)
        request = tornado.httpclient.HTTPRequest(cfg.DB_SERVER + '/srvStat', method='POST', body=j_stat)
        self.db_client.fetch(request, callback=self._do_nothing)

        self._stat_read_count = 0
        self._stat_write_count = 0

    def _do_nothing(self, respond):
        pass

    '''-----------------------------------x--'''

    def get_record__old(self, user_uid):
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

    def commit_dirty_record__old(self, user_uid, dirty_record_str):
        dirty_record_dict = json.JSONDecoder().decode(dirty_record_str)

        if user_uid not in self.batch:
            server_log.error('new dict')
            self.batch[user_uid] = dict()

        self.batch[user_uid].update(dirty_record_dict)

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



