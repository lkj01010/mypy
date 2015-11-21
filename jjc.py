# -*- coding: UTF-8 -*-
import datetime
import tornado.httpclient
import tornado.ioloop
import cfg
import pymongo
import json
from log import server_log
from collections import OrderedDict
import random
from copy import deepcopy
from gamecfg.jjc_grade import GRADE, grade_index_by_honour
from gamecfg.jjc_rank import RANK
from dbdata_pusher import DBData, DBDataPusher

class _PlayerInfo:
    def __init__(self, data):
        if data and type(data) == dict:
            self.data = data
        else:
            self.data = {'user_uid': '',
                         'honour': 0,
                         'honour_day': 0,
                         'win': 0,
                         'win_day': 0,
                         'lose': 0,
                         'lose_day': 0,
                         'comb': 0,
                         'grade': 0,
                         'grade_got': 0}
            server_log.error('[jjc error] should not gen user data there.')
        self.rank = 10000000

    def update(self, player_info, rank):
        self.data = player_info.data
        self.rank = rank

    def load_from_dict(self, string):
        pass

    def dump_to_dict(self):
        pass

class JJC:

    _COMB_HONOUR_1 = 10
    _COMB_HONOUR_3 = 20
    _COMB_HONOUR_6 = 30
    _TOP_PLAYER_COUNT = 30

    # _RANK_REWARD__SYN_INTERVAL = 5 * 60 * 1000
    _RANK_REWARD__SYN_INTERVAL = 5 * 60 * 1000
    _BALANCE_CHECK_INTERVAL = 60 * 1000
    _BALANCE_HOUR = 9

    def __init__(self, db, record_mod):

        self.db = db
        self._record_mod = record_mod

        # save player by user_uid
        self._player_dict = dict()
        self._rank_list = list()

        # _is_match_front is turn over in each find_opponent call
        self._is_match_front = True
        # self._test_add_data()
        self._gen_ranklist_from_db()

        self._rank_reward_batch = dict()
        self._load_rank_reward()
        rank_reward_pusher = DBDataPusher(self._record_mod.db_client, cfg.DB_SERVER + '/db', 'jjc.rank_reward',
                                          self._rank_reward_batch, JJC.rank_reward_item_gen,
                                          JJC._RANK_REWARD__SYN_INTERVAL)
        rank_reward_pusher.start()

        self._jjc_srvinfo = self.db.srvinfo.find_one({'type': 'jjc'}, {'_id': False})
        if not self._jjc_srvinfo:
            self._jjc_srvinfo = {'type': 'jjc'}
            self.db.srvinfo.insert_one(self._jjc_srvinfo)

        # [[
        # balance_timer = tornado.ioloop.PeriodicCallback(self._check_balance_rank_reward, JJC._BALANCE_CHECK_INTERVAL)
        # balance_timer.start()
        # -----------------> temp test
        balance_timer = tornado.ioloop.PeriodicCallback(self.test_check_balance_rank_reward, 1 * 60 * 1000)
        balance_timer.start()
        # ]]

        pass

    def _test_add_data(self):
        self.db.jjc.drop()
        for i in range(1, 100):
            self.db.jjc.insert({'user_uid': 'user' + str(i), 'honour_day': random.randint(0, 100)})

    def _gen_ranklist_from_db(self):
        cursor = self.db.user.find({}, projection={ '_id': False,
                                                    'user_uid': True,
                                                    'record.jjc': True,
                                                    # 'record.jjc.win': True,
                                                    # 'record.jjc.lose': True,
                                                    # 'record.jjc.honour': True,
                                                    # 'record.jjc.win_day': True,
                                                    # 'record.jjc.lose_day': True,
                                                    # 'record.jjc.honour_day': True,
                                                    # 'record.jjc.grade': True,
                                                    # 'record.jjc.comb': True
                                                    })
        temp_dict = dict()
        for doc in cursor:

            if 'record' in doc and doc['record']['jjc']['honour_day'] > 0:
                data = dict()
                data['user_uid'] = doc['user_uid']
                data['win'] = doc['record']['jjc']['win']
                data['win_day'] = doc['record']['jjc']['win_day']
                data['lose'] = doc['record']['jjc']['lose']
                data['lose_day'] = doc['record']['jjc']['lose_day']
                data['honour'] = doc['record']['jjc']['honour']
                data['honour_day'] = doc['record']['jjc']['honour_day']
                data['comb'] = doc['record']['jjc']['comb']
                data['grade'] = doc['record']['jjc']['grade']
                data['grade_got'] = doc['record']['jjc']['grade_got']

                info = _PlayerInfo(data)
                self._player_dict[doc['user_uid']] = info

                temp_dict[data['user_uid']] = data['honour_day']

        honour_dict = OrderedDict(sorted(temp_dict.items(), key=lambda x: x[1], reverse=True))

        rank = 1
        for k in honour_dict:
            self._rank_list.append(self._player_dict[k])
            self._player_dict[k].rank = rank
            rank += 1
        for v in self._rank_list:
            print v.data['user_uid'], v.data['honour_day'], v.rank, '------------'

    def _load_rank_reward(self):
        cursor = self.db.jjc.rank_reward.find({}, projection={'_id': False})
        for doc in cursor:
            user_uid = doc['user_uid']
            self._rank_reward_batch[user_uid] = DBData()
            self._rank_reward_batch[user_uid]['coin'] = doc['reward']['coin']
            self._rank_reward_batch[user_uid]['zuan'] = doc['reward']['zuan']
            self._rank_reward_batch[user_uid]['rank'] = doc['reward']['rank']

    def set_user_jjcdata(self, user_uid, data):
        info = _PlayerInfo(data)
        info.data['user_uid'] = user_uid
        info.rank = len(self._rank_list) + 1    # last rank
        self._rank_list.append(info)
        self._player_dict[user_uid] = info
        server_log.info("[jjc] new add user_uid=" + user_uid + ' rank=' + str(info.rank))

    def _update_player_in_rank(self, user_uid, is_toward_front):
        """should handle_match_result first, player must in both player_dict and rank_list
        """
        try:
            player_info = self._player_dict[user_uid]

            rank_now = player_info.rank

            if is_toward_front:
                # find award
                while True:
                    rank_front = rank_now - 1
                    if rank_front > 0:
                        info_front = self._rank_list[rank_front - 1]
                        if info_front.data['honour_day'] < player_info.data['honour_day']:
                            info_front.rank += 1
                            rank_now -= 1
                        else:
                            break
                    else:
                        break
            else:
                # find back
                last_rank = len(self._rank_list)
                while True:
                    rank_back = rank_now + 1
                    if rank_back <= last_rank:
                        info_back = self._rank_list[rank_back - 1]
                        if info_back.data['honour_day'] > player_info.data['honour_day']:
                            info_back.rank -= 1
                            rank_now += 1
                        else:
                            break
                    else:
                        break

            if player_info.rank == rank_now:
                pass
            else:
                # del old and insert to destination
                player_info_dest = deepcopy(player_info)
                player_info_dest.rank = rank_now
                del self._rank_list[player_info.rank - 1]
                self._player_dict[player_info_dest.data['user_uid']] = player_info_dest
                self._rank_list.insert(rank_now - 1, player_info_dest)

        except KeyError:
            server_log.error("[error]_update_player_in_rank, KeyError.")

    def _get_jjc_player_info(self, user_uid):
        if user_uid in self._player_dict:
            info = self._player_dict[user_uid]
        else:
            # new user push to the end of rank_list
            user_record = self._record_mod.get_user_data(user_uid)
            jjc_data = deepcopy(user_record['jjc'])
            del jjc_data['jjc_cfg']
            info = _PlayerInfo(jjc_data)
            info.data['user_uid'] = user_uid
            info.rank = len(self._rank_list) + 1    # last rank
            self._player_dict[user_uid] = info
            self._rank_list.append(info)
            server_log.info("[jjc]new add user_uid=" + user_uid + ' rank=' + str(info.rank))
        return info

    def _update_jjc_data_to_record(self, user_uid, data):
        user_record = self._record_mod.get_user_data(user_uid)
        user_record['jjc'].update(data)
        del user_record['jjc']['user_uid']

    def handle_match_result(self, user_uid, is_win):
        info = self._get_jjc_player_info(user_uid)

        if is_win == 1:
            is_toward_front = True
            info.data['win'] += 1
            info.data['win_day'] += 1
            info.data['comb'] += 1

            if info.data['comb'] <= 2:
                honour = JJC._COMB_HONOUR_1
            elif info.data['comb'] < 6:
                honour = JJC._COMB_HONOUR_3
            else:
                honour = JJC._COMB_HONOUR_6
        else:
            is_toward_front = False
            info.data['lose'] += 1
            info.data['lose_day'] += 1
            info.data['comb'] = 0
            honour = 1

        info.data['honour'] += honour
        info.data['honour_day'] += honour
        info.data['grade'] = grade_index_by_honour(info.data['honour']) + 1

        self._update_player_in_rank(user_uid, is_toward_front)

        reply_dict = deepcopy(info.data)
        reply_dict['is_win'] = is_win

        self._update_jjc_data_to_record(user_uid, info.data)

        return reply_dict

    def handle_jjc_ranks(self, user_uid):
        top_list = self._rank_list[:30]
        print str(top_list)
        reply_list = list()
        for v in self._rank_list[:30]:
            player = dict()
            player['rank'] = v.rank
            player['user_uid'] = v.data['user_uid']
            player['win_day'] = v.data['win_day']
            player['lose_day'] = v.data['lose_day']
            player['honour_day'] = v.data['honour_day']
            player['grade'] = v.data['grade']

            user_record = self._record_mod.get_user_data(v.data['user_uid'])
            if 'zone' in user_record:
                player['nickname'] = user_record['zone']['nickname']
                player['figureurl'] = user_record['zone']['figureurl']

            reply_list.append(player)
        if user_uid in self._player_dict:
            user_rank = self._player_dict[user_uid].rank
        else:
            # stand for not in ranks
            user_rank = -1
        reply_dict = {
            'tops': reply_list,
            'self_rank': user_rank
        }
        return reply_dict

    def handle_find_opponent(self, user_uid):
        """ return None when not found opponent
        """
        info = self._get_jjc_player_info(user_uid)

        back_count = len(self._rank_list) - info.rank
        dest_rank = JJC._make_match_seed_by_rank(info.rank, back_count, self._is_match_front)
        if dest_rank:
            oppo_user_uid = self._rank_list[dest_rank - 1].data['user_uid']
            server_log.info("[jjc] user_uid=" + user_uid + ' rank=' + str(info.rank) + ' found opponent user_uid=' +
                        oppo_user_uid + ' rank=' + str(dest_rank))
            return oppo_user_uid
        else:
            server_log.warning('[jjc] not found opponent, user_uid=' + user_uid + ' rank=' + str(info.rank))
            return None

    @staticmethod
    def _make_match_seed_by_rank(rank, back_count, is_front):
        """ return 0: not found
        """

        if rank > 500:
            fs_range = 100
        elif rank > 100:
            fs_range = 40
        elif rank > 30:
            fs_range = 10
        elif rank > 10:
            fs_range = 6
        elif rank > 3:
            fs_range = 3
        else:
            fs_range = 1

        front_count = rank - 1

        if is_front:
            if front_count == 0:
                if back_count == 0:     # only user himself
                    return 0            # not found
                else:
                    if back_count < 30:
                        fs_range = back_count
                    else:
                        fs_range = 30

                    offset = random.randint(1, fs_range)
                    return rank + offset
            else:
                if fs_range > front_count:
                    fs_range = front_count

                offset = random.randint(1, fs_range)
                return rank - offset

        else:   # is_back
            if back_count == 0:
                if front_count == 0:
                    return 0
                else:
                    if front_count < 30:
                        fs_range = front_count
                    else:
                        fs_range = 30

                    offset = random.randint(1, fs_range)
                    return rank - offset
            else:
                if fs_range > back_count:
                    fs_range = back_count

                offset = random.randint(1, fs_range)
                return rank + offset

    def handle_jjc_grade_reward(self, user_uid):
        # TODO: add reward in client, security issue

        info = self._get_jjc_player_info(user_uid)
        reward = dict()
        if info.data['grade_got'] < info.data['grade']:
            reward_cfg = GRADE[info.data['grade_got']]
            reward['coin'] = reward_cfg['-CoinReward']
            reward['zuan'] = reward_cfg['-DiamondReward']
            reward['card'] = reward_cfg['-CardReward']

            info.data['grade_got'] += 1
            reward['grade_got'] = info.data['grade_got']

            self._update_jjc_data_to_record(user_uid, info.data)
        return reward

    def handle_jjc_rank_reward(self, user_uid):
        reply_dict = dict()
        if user_uid in self._rank_reward_batch:
            reward = self._rank_reward_batch[user_uid]
            reply_dict['coin'] = reward['coin']
            reply_dict['zuan'] = reward['zuan']
            reply_dict['rank'] = reward['rank']
            del self._rank_reward_batch[user_uid]
        return reply_dict

    def _check_balance_rank_reward(self):
        now = datetime.datetime.now()
        is_need_balance = False
        if 21 < now.hour:
            if 'last__rank_reward__time' not in self._jjc_srvinfo:
                self._jjc_srvinfo['last__rank_reward__time'] = now
                is_need_balance = True
            else:
                if self._jjc_srvinfo['last__rank_reward__time'].day < now.day \
                        or self._jjc_srvinfo['last__rank_reward__time'].month < now.month \
                        or self._jjc_srvinfo['last__rank_reward__time'].year < now.year:
                    server_log.info('[jjc] will do balance, last day is ' + str(self._jjc_srvinfo['last__rank_reward__time'].day))
                    self._jjc_srvinfo['last__rank_reward__time'] = now
                    is_need_balance = True

        if is_need_balance:
            self._balance_rank_reward()

    def test_check_balance_rank_reward(self):
        now = datetime.datetime.now()
        is_need_balance = False
        if 6 < now.hour:
            if 'TEST_last__rank_reward__time' not in self._jjc_srvinfo:
                self._jjc_srvinfo['TEST_last__rank_reward__time'] = now
                is_need_balance = True
            else:
                # if self._jjc_srvinfo['TEST_last__rank_reward__time'].hour != now.hour:
                minute = self._jjc_srvinfo['TEST_last__rank_reward__time'].minute
                if minute % 2 == 0:
                    server_log.info('[jjc] will do balance, last day is ' + str(self._jjc_srvinfo['TEST_last__rank_reward__time'].day) \
                               + 'last hour is ' + str(self._jjc_srvinfo['TEST_last__rank_reward__time'].day))
                    self._jjc_srvinfo['TEST_last__rank_reward__time'] = now
                    is_need_balance = True

        if is_need_balance:
            self._balance_rank_reward()

    def _balance_rank_reward(self):
        self.db.srvinfo.replace_one({'type': 'jjc'}, self._jjc_srvinfo)
        for reward_mod in RANK:
            for player_tuple in enumerate(self._rank_list[reward_mod['-RankTop'] - 1:reward_mod['-RankLast']]):
                # rank
                slice_index = player_tuple[0]
                rank = reward_mod['-RankTop'] + slice_index

                # player info
                player = player_tuple[1]
                user_uid = player.data['user_uid']
                if user_uid not in self._rank_reward_batch:
                    self._rank_reward_batch[user_uid] = DBData()
                    self._rank_reward_batch[user_uid]['coin'] = 0
                    self._rank_reward_batch[user_uid]['zuan'] = 0
                self._rank_reward_batch[user_uid]['coin'] += reward_mod['-CoinReward']
                self._rank_reward_batch[user_uid]['zuan'] += reward_mod['-DiamondReward']
                self._rank_reward_batch[user_uid]['rank'] = rank
                self._rank_reward_batch[user_uid].touch += 1

        # syn to record
        for user_uid, info in self._player_dict.items():
            info.data['win_day'] = 0
            info.data['lose_day'] = 0
            info.data['honour_day'] = 0
            self._update_jjc_data_to_record(user_uid, info.data)

        # clean rankings
        self._player_dict = dict()
        self._rank_list = list()

    @staticmethod
    def rank_reward_item_gen(user_uid, reward):
        item = dict()
        item['filter'] = {'user_uid': user_uid}
        if reward['coin'] > 0 and reward['zuan'] > 0:
            item['modifier'] = 'set'
            item['update'] = {'key': 'reward',
                              'value': {'coin': reward['coin'],
                                        'zuan': reward['zuan'],
                                        'rank': reward['rank']
                                        }
                              }
        else:
            item['modifier'] = 'delete'
        return item


if __name__ == "__main__":
    # jjc = JJC('192.168.1.250', 27017)
    conn = pymongo.MongoClient('42.62.101.24', 27017)
    jjc = JJC(conn.dota)
