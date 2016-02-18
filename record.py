# -*- coding: UTF-8 -*-

import tornado.httpclient
import tornado.ioloop

import pymongo
import json
from log import server_log
import time
import random
import copy
import datetime

import cfg
import db_key
from db_pusher import DataHolder, DBPusher
import jjc


class Record(object):

    _RECORD_SYN_INTERVAL = 5 * 60 * 1000    # 5*60*1000
    _RECORD_CLEAN_INACTIVE_INTERVAL = 30 * 60 * 1000
    _STAT_INTERVAL = 15 * 60 * 1000

    def __init__(self, user_zone_info_cache):
        self._user_zone_info_cache = user_zone_info_cache

        conn = pymongo.MongoClient(cfg.srvcfg['ip_mongodb'], cfg.srvcfg['port_mongodb'])

        db_key.fill_keys()

        self.db = conn[cfg.srvcfg['dbname_mongodb']]
        # self.db.user.drop_index('_id') #  drop '_id' is invalid
        self.db.user.create_index('user_uid')
        self.db.mail.create_index('user_uid')
        self.db_client = tornado.httpclient.AsyncHTTPClient()



        """record save in"""
        self.cache = dict()

        record_db_pusher = DBPusher(self.db_client, cfg.srvcfg['addr_db'] + '/recordBatch', self.cache,
                                    Record._RECORD_SYN_INTERVAL,
                                    Record._RECORD_CLEAN_INACTIVE_INTERVAL)
        record_db_pusher.start()

        # time_task = tornado.ioloop.PeriodicCallback(self.push_dirty_records_to_db, Record._RECORD_SYN_INTERVAL)
        # time_task.start()
        #
        # time_task2 = tornado.ioloop.PeriodicCallback(self._clean_inactive_records,
        #                                              Record._RECORD_CLEAN_INACTIVE_INTERVAL)
        # time_task2.start()

        # jjc model
        self._jjc_mod = jjc.JJC(self.db, self)

        '''channel ascp'''
        self._username_cache = set()

        '''travel all item in user to process some model'''
        self._travel_user_record()


        # # event handler
        # self._event_timer = tornado.ioloop.PeriodicCallback(self._check_time_event, 5 * 1000)
        # self._event_timer.start()
        # self._time_events = dict()
        # self._last_time = datetime.datetime.time()
        # self._time_events['jjc_daily_account'] = {
        #     'trigger': datetime.time(21, 0, 0),
        #     'callback': self._jjc_mod.balance_rank_reward
        # }

        # stat
        self._stat_write_count = 0
        self._stat_read_count = 0
        time_task3 = tornado.ioloop.PeriodicCallback(self._stat_active_user, Record._STAT_INTERVAL)
        time_task3.start()

    # def _check_time_event(self):
    #     now = datetime.time()
    #     for k, v in self._time_events.items():
    #         trigger = v['trigger']
    #         if self._last_time < trigger < now:
    #             v['callback']()

    def _travel_user_record(self):
        if cfg.srvcfg['channel'] == 2:
            cursor = self.db.user.find({}, projection={'_id': False,
                                                       'user_uid': True,
                                                       'record.nickname': True,
                                                       })
            for doc in cursor:
                rec = doc['record']
                self._username_cache.add(rec['nickname'])

    def get_user_data(self, user_uid):
        if user_uid in self.cache:
            return self.cache[user_uid].data
        else:
            """fix me:
                db synchronous operation. could do it asynchronous if it is hotpot
            """
            find_ret = self.db.user.find_one({'user_uid': user_uid}, {'_id': False, 'create_time': False})
            if find_ret:
                reply_dict = find_ret['record']
                self.cache[user_uid] = DataHolder(reply_dict)
            else:
                reply_dict = dict()
                # reply_dict['user_uid'] = user_uid
                reply_dict['record'] = db_key.default_record()
                reply_dict['record']['userno'] = self._make_userno()

                """ AVOID TO: do db operation during server running !
                    it may cause long synchronous delay when db is busy !
                """
                # self.db.user.insert(reply_dict)     # this oper will add '_id' item !!!

                server_log.warning('cache size=%d, not found, new user_uid=%s' % (len(self.cache), user_uid))
                reply_dict = reply_dict['record']

                self.cache[user_uid] = DataHolder(reply_dict)
                self.cache[user_uid].touch += 1

            return reply_dict

    def touch_user_data(self, user_uid):
        """touch data, so it will push to db server
        """
        if user_uid in self.cache:
            data_holder = self.cache[user_uid]
            data_holder.touch += 1
        else:
            find_ret = self.db.user.find_one({'user_uid': user_uid}, {'_id': False, 'create_time': False})
            if find_ret:
                reply_dict = find_ret['record']
                self.cache[user_uid] = DataHolder(reply_dict)
                self.cache[user_uid].touch += 1
            server_log.error('[record] touch user not in cache: ' + user_uid)

    def get_record(self, user_uid):
        """return a record (dict type)"""
        self._stat_read_count += 1

        record = self.get_user_data(user_uid)

        """new player"""
        if record['v_-1'] == 0:
            record['v_-1'] = 1

        # update zone info
        if cfg.srvcfg['channel'] == 1:
            user_id = user_uid[:-2]
            if user_id in self._user_zone_info_cache:
                zone_info = self._user_zone_info_cache[user_id]
                record['zone']['nickname'] = zone_info['nickname']
                record['zone']['figureurl'] = zone_info['figureurl']

        # check time logic
        self._jjc_mod.data_check(user_uid, record)

        # reset daily
        now = datetime.datetime.now()
        if record['day'] != now.day or record['month'] != now.month:
            record['shareTimes'] = 0

        # update time
        record['month'] = now.month
        record['day'] = now.day
        record['hour'] = now.hour

        # month card
        if record['srv']['smcard'] != 0:
            smcard_deadline = datetime.datetime.strptime(record['srv']['smcard'], "%Y-%m-%d-%H-%M")
            if smcard_deadline > now:
                record['smcardleft'] = (smcard_deadline - now).days + 1
            else:
                record['smcardleft'] = 0
        else:
            record['smcardleft'] = 0

        if record['srv']['gmcard'] != 0:
            gmcard_deadline = datetime.datetime.strptime(record['srv']['gmcard'], "%Y-%m-%d-%H-%M")
            if gmcard_deadline > now:
                record['gmcardleft'] = (gmcard_deadline - now).days + 1
            else:
                record['gmcardleft'] = 0
        else:
            record['gmcardleft'] = 0

        # offline second -> for guaji
        record['offlinesec'] = (now - datetime.datetime.strptime(
            record['modify_time'], "%Y-%m-%d-%H-%M")).total_seconds()

        # rm srv data
        reply_dict = copy.deepcopy(record)
        del reply_dict['srv']
        del reply_dict['modify_time']

        # send access info to gate srv
        access_dict = dict()
        access_dict['type'] = 'last_access'
        access_dict['body'] = {
            'user_uid': user_uid,
            'region_id': cfg.remote_type
        }
        j_stat = json.JSONEncoder().encode(access_dict)
        request = tornado.httpclient.HTTPRequest(cfg.srvcfg['addr_stat'] + '/rec', method='POST', body=j_stat)
        self.db_client.fetch(request, callback=self._do_nothing)

        return reply_dict

    def commit_record(self, user_uid, dirty_record_str):
        self._stat_write_count += 1
        dirty_record_dict = json.JSONDecoder().decode(dirty_record_str)
        # if user_uid in self.cache:  # normal
        #     self.cache[user_uid].data.update(dirty_record_dict)
        #     self.cache[user_uid].touch += 1
        # else:   # abnormal! error!
        #     # warning: nearly most time, user should in cache, but not!
        #     server_log.warning('warning: nearly most time, user should in cache, but not! user_uid=' + user_uid)
        #     find_ret = self.db.user.find_one({'user_uid': user_uid})
        #     if find_ret:
        #         del find_ret['_id']
        #         if 'create_time' in find_ret:
        #             del find_ret['create_time']
        #         reply_dict = find_ret['record']
        #         reply_dict.update(dirty_record_dict)
        #         self.cache[user_uid] = _DataHolder(reply_dict)
        #         self.cache[user_uid].touch += 1
        #     else:
        #         server_log.error('error: commit record, but user not found!!!')
        user_data_dict = self.get_user_data(user_uid)
        if user_data_dict['v_-1'] == 0:
            server_log.error('error: commit record, user not exist!!!')
            return False
        else:
            user_data_dict.update(dirty_record_dict)
            user_data_dict['modify_time'] = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
            self.cache[user_uid].touch += 1
            return True

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
        request = tornado.httpclient.HTTPRequest(cfg.srvcfg['addr_db'] + '/srvStat', method='POST', body=j_stat)
        self.db_client.fetch(request, callback=self._do_nothing)

        self._stat_read_count = 0
        self._stat_write_count = 0

    def _do_nothing(self, respond):
        pass

    def remove_from_cache(self, user_uid):
        try:
            del self.cache[user_uid]
        except KeyError:
            server_log.error('remove_from_cache, user_uid=' + user_uid + 'not exist.')

    def handle_req(self, user_uid, req):
        # try:
        req_dict = json.JSONDecoder().decode(req)
        cmd = req_dict['cmd']
        if 'body' in req_dict:
            body = req_dict['body']
        else:
            body = dict()

        if cmd == 'get_mail':
            reply_dict = self._handle_get_mail(user_uid)
        elif cmd == 'jjc_ret':
            reply_dict = self._handle_jjc_ret(user_uid, body)
        elif cmd == 'jjc_find':
            reply_dict = self._handle_jjc_find(user_uid, body)
        elif cmd == 'jjc_ranks':
            reply_dict = self._handle_jjc_ranks(user_uid)
        elif cmd == 'jjc_grade_reward':
            reply_dict = self._handle_jjc_grade_reward(user_uid)
        elif cmd == 'buy_mcard':
            reply_dict = self._handle_buy_mcard(user_uid, body)
        elif cmd == 'acc_pay':
            reply_dict = self._handle_acc_pay(user_uid, body)
        elif cmd == 'reset_continue_pay':
            reply_dict = self._handle_reset_continue_pay(user_uid)
        elif cmd == 'set_nickname_and_headidx':
            reply_dict = self._handle_set_nickname_and_headidx(user_uid, body)
        elif cmd == 'can_share':
            reply_dict = self._handle_can_share(user_uid)
        elif cmd == 'share':
            reply_dict = self._handle_share(user_uid)
        reply_dict['ret'] = 1

        # except KeyError:
        #     reply_dict = {'ret': 0}
        #     server_log.error('handle_req, KeyError.')

        return reply_dict

    def _handle_get_mail(self, user_uid):
        mail_dict = dict()
        mail_dict['jjc_rank_reward'] = self._jjc_mod.handle_jjc_rank_reward(user_uid)
        return mail_dict

    def _handle_jjc_ret(self, user_uid, body):
        # handle jjc logic
        reply_dict = self._jjc_mod.handle_match_result(user_uid, body['is_win'])
        return reply_dict

    def _handle_jjc_find(self, user_uid, body):
        user_data = self.get_user_data(user_uid)

        user_data['jjc']['jjc_cfg'] = body['jjc_cfg']

        reply_dict = self.__do_jjc_find(user_uid)
        server_log.info('[jjc] return str: ' + str(reply_dict))
        return reply_dict

    def __do_jjc_find(self, user_uid):
        opponent_uid = self._jjc_mod.handle_find_opponent(user_uid)

        # [[
        # opponent_data = self.get_user_data(opponent_uid)
        # if opponent_uid:
        #     reply_dict = dict()
        #     reply_dict['user_uid'] = opponent_uid
        #     reply_dict['jjc_cfg'] = opponent_data['jjc_cfg']
        #     return reply_dict
        # else:
        #     return self.__do_jjc_find(user_uid)
        # =====================>

        if opponent_uid:
            opponent_data = self.get_user_data(opponent_uid)
            reply_dict = dict()
            reply_dict['user_id'] = opponent_uid[0:-2]
            reply_dict['nickname'] = opponent_data['zone']['nickname']
            reply_dict['figureurl'] = opponent_data['zone']['figureurl']
            reply_dict['jjc_cfg'] = opponent_data['jjc']['jjc_cfg']
            reply_dict['r_exp'] = opponent_data['r_exp']

            if cfg.srvcfg['channel'] == 2:
                reply_dict['headidx'] = opponent_data['headidx']
                reply_dict['nickname'] = opponent_data['nickname']

            return reply_dict
        else:
            return self._jjc_mod.handle_jjc_ranks(user_uid)
        # ]]

    def _handle_jjc_ranks(self, user_uid):
        return self._jjc_mod.handle_jjc_ranks(user_uid)

    def _handle_jjc_grade_reward(self, user_uid):
        reply_dict = self._jjc_mod.handle_jjc_grade_reward(user_uid)
        return reply_dict

    def _handle_buy_mcard(self, user_uid, body):
        user_data = self.get_user_data(user_uid)
        deadline = datetime.datetime.now() + datetime.timedelta(days=30)
        deadline = deadline.replace(hour=0, minute=0, second=0)
        if body['type'] == 1:
            key = 'gmcard'
            user_data['gmcardleft'] = 30
        else:
            key = 'smcard'
            user_data['smcardleft'] = 30
        user_data['srv'][key] = deadline.strftime("%Y-%m-%d-%H-%M")
        self.cache[user_uid].touch += 1

        reply_dict = dict()
        reply_dict['type'] = key
        reply_dict['leftday'] = 30
        return reply_dict

    def _handle_acc_pay(self, user_uid, body):
        self.cache[user_uid].touch += 1
        user_data = self.get_user_data(user_uid)

        '''累积充值'''
        user_data['acc_pay'] += body['amount']

        '''日连续充值'''
        lastday_str = user_data['srv']['lastConsumeDay']
        today = datetime.datetime.today()
        today_str = today.strftime('%Y-%m-%d')
        yesterday = today + datetime.timedelta(days=-1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        server_log.info('_handle_acc_pay, lastday_str=' + lastday_str + ', yesterday_str=' +
                        yesterday_str)

        if lastday_str == '':
            user_data['continue_pay'] = 1
            user_data['srv']['lastConsumeDay'] = today_str
        elif lastday_str == today_str:
            pass
        elif lastday_str == yesterday_str:
            user_data['continue_pay'] += 1
            user_data['srv']['lastConsumeDay'] = today_str
        else:
            user_data['continue_pay'] = 0
            user_data['srv']['lastConsumeDay'] = today_str

        reply_dict = dict()
        reply_dict['acc_pay'] = user_data['acc_pay']
        reply_dict['continue_pay'] = user_data['continue_pay']
        return reply_dict

    def _handle_reset_continue_pay(self, user_uid):
        '''没办法，充值奖励客户端服务器功能要一天写完，只能这样了。奖励重置的其他部分在客户端'''
        self.cache[user_uid].touch += 1
        user_data = self.get_user_data(user_uid)

        user_data['continue_pay'] = 1
        today = datetime.datetime.today()
        today_str = today.strftime('%Y-%m-%d')
        user_data['srv']['lastConsumeDay'] = today_str

        return dict()

    def _handle_set_nickname_and_headidx(self, user_uid, body):
        reply_dict = dict()
        if body['nickname'] in self._username_cache:
            reply_dict['unique'] = 0
        else:
            self._username_cache.add(body['nickname'])

            reply_dict['unique'] = 1
            reply_dict['nickname'] = body['nickname']
            reply_dict['headidx'] = body['headidx']

        # if reply_dict['unique'] == 1:
            self.cache[user_uid].touch += 1
            user_data = self.get_user_data(user_uid)
            user_data['nickname'] = body['nickname']
            user_data['headidx'] = body['headidx']

        return reply_dict

    def _handle_can_share(self, user_uid):
        reply_dict = dict()

        user_data = self.get_user_data(user_uid)
        if user_data['shareTimes'] >= 3:
            reply_dict['can'] = 0
        else:
            if user_data['shareTimes'] >= 1:
                last_share = user_data['lastShareTime']
                now = datetime.datetime.now()
                interval = (now - datetime.datetime.strptime(
                    last_share, "%Y-%m-%d-%H-%M")).total_seconds()
                if interval < 2 * 3600:
                    reply_dict['can'] = -1
                    reply_dict['leftsec'] = 2 * 3600 - interval
                else:
                    reply_dict['can'] = 1
            else:
                reply_dict['can'] = 1
        return reply_dict

    def _handle_share(self, user_uid):
        reply_dict = dict()

        self.cache[user_uid].touch += 1
        user_data = self.get_user_data(user_uid)

        if user_data['shareTimes'] >= 3:
            reply_dict['ok'] = False
        else:
            user_data['lastShareTime'] = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
            user_data['shareTimes'] += 1
            reply_dict['ok'] = True
        return reply_dict

    '''-----------------------------------x--'''

    # def get_record__old(self, user_uid):
    #     # server_log.info('get record. user_uid=' + user_uid)
    #     # if user_uid not in self.cache:
    #     #     server_log.info('not in cache')
    #
    #         find_ret = self.db.user.find_one({'user_uid': user_uid})
    #
    #         if find_ret:
    #             server_log.info('db find')
    #             del find_ret['_id']
    #             reply_dict = dict()
    #             if 'record' in find_ret and type(find_ret['record']) is dict:
    #                 # reply_dict = dict((key.encode('ascii'), value) for key, value in find_ret['record'].items())
    #                 reply_dict = find_ret['record']
    #
    #             """attach unpushed record item to Record(old) from db"""
    #             if user_uid in self.batch_on_pushing:
    #                 server_log.warning('attach record_on_pushing: ' + user_uid +
    #                                 ', record: ' + str(self.batch_on_pushing[user_uid]))
    #                 reply_dict.update(self.batch_on_pushing[user_uid])
    #             if user_uid in self.batch:
    #                 server_log.info('attach record_batch: ' + user_uid +
    #                                 ', record: ' + str(self.batch[user_uid]))
    #                 reply_dict.update(self.batch[user_uid])
    #
    #             """add unique number id"""
    #             if 'userno' not in reply_dict:
    #                 reply_dict['userno'] = self._make_userno()
    #         else:
    #             server_log.info('not find record of user_uid=' + user_uid + ', make default record !!!')
    #             record_doc = dict()
    #             record_doc['user_uid'] = user_uid
    #             record_doc['record'] = Record._default_record()
    #             record_doc['record']['userno'] = self._make_userno()
    #             self.db.user.insert(record_doc)
    #             reply_dict = record_doc['record']
    #
    #         return reply_dict
    #
    # def commit_dirty_record__old(self, user_uid, dirty_record_str):
    #     dirty_record_dict = json.JSONDecoder().decode(dirty_record_str)
    #
    #     if user_uid not in self.batch:
    #         server_log.error('new dict')
    #         self.batch[user_uid] = dict()
    #
    #     self.batch[user_uid].update(dirty_record_dict)
    #
    #     if user_uid in self.batch_on_pushing:
    #         self.batch_on_pushing[user_uid].update(dirty_record_dict)
    #
    # def push_records_to_db(self):
    #     j_record_batch = json.JSONEncoder().encode(self.batch)
    #     # server_log.error('push batch: ' + j_record_batch)
    #     request = tornado.httpclient.HTTPRequest(cfg.DB_SERVER, method='POST', body=j_record_batch)
    #     self.db_client.fetch(request, callback=self.push_records_to_db_callback)
    #
    #     self.batch_on_pushing = copy.deepcopy(self.batch)
    #     self.batch.clear()
    #
    # def push_records_to_db_callback(self, response):
    #     if response.body:
    #         self.batch_on_pushing.clear()
    #         # server_log.info('syn response: ' + str(response.body))
    #     else:
    #         # TODO : error handle: 备份没有提交的 on_push 到现有的 batch 上
    #         self.batch_on_pushing.update(self.batch)
    #         self.batch = copy.deepcopy(self.batch_on_pushing)
    #         self.batch_on_pushing.clear()
    #         server_log.info('push error !!!!!!!!!!!!! syn response: ' + str(response.body))
