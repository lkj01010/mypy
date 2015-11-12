# -*- coding: UTF-8 -*-

import pymongo
import json
from log import server_log
from collections import OrderedDict
import random
from copy import deepcopy

class _PlayerInfo:
    def __init__(self, data):
        if data and type(data) == dict:
            self.data = data
        else:
            self.data = {'user_uid': '', 'honour': 0}
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
    _COMB_HONOUR_2 = 20
    _COMB_HONOUR_10 = 30
    _TOP_PLAYER_COUNT = 30

    def __init__(self, db):

        self.db = db

        # save player by user_uid
        self._player_dict = dict()
        self._rank_list = list()

        # _is_match_front is turn over in each find_opponent call
        self._is_match_front = True
        # self._test_add_data()
        self._load_from_db()
        pass

    def _test_add_data(self):
        self.db.jjc.drop()
        for i in range(1, 100):
            self.db.jjc.insert({'user_uid': 'user' + str(i), 'honour_day': random.randint(0, 100)})

    def _load_from_db(self):
        cursor = self.db.jjc.find({}, projection={ '_id': False,
                                                    'user_uid': True,
                                                    'win': True,
                                                    'lose': True,
                                                    'honour': True,
                                                    'win_day': True,
                                                    'lose_day': True,
                                                    'honour_day': True,
                                                    'comb': True
                                                    }).sort([('honour_day', 1)])
        temp_dict = dict()
        for doc in cursor:
            info = _PlayerInfo(doc)
            if 'honour_day' in doc:
                temp_dict[doc['user_uid']] = doc['honour_day']
                self._player_dict[doc['user_uid']] = info
                print str(doc)

        for k in temp_dict:
            print k, temp_dict[k]

        honour_dict = OrderedDict(sorted(temp_dict.items(), key=lambda x: x[1], reverse=True))

        rank = 1
        for k in honour_dict:
            self._rank_list.append(self._player_dict[k])
            self._player_dict[k].rank = rank
            rank += 1

        for v in self._rank_list:
            print v.data['user_uid'], v.data['honour_day'], v.rank, '------------'

        pass

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
                    if rank_front >= 0:
                        info_front = self._rank_list[rank_front - 1]
                        if info_front.data['honour_day'] < player_info.data['honour_day']:
                            info_front.data.rank += 1
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
                    if rank_back <= len(self._rank_list):
                        info_back = self._rank_list[rank_back - 1]
                        if info_back.data['honour_day'] > player_info.data['honour_day']:
                            info_back.data.rank -= 1
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
                self._rank_list.insert(rank_now - 1)

        except KeyError:
            server_log.error("[error]_update_player_in_rank, KeyError.")

    def handle_match_result(self, user_uid, is_win):
        if 'user_uid' in self._player_dict:
            info = self._player_dict[user_uid]
        else:
            # new user push to the end of rank_list
            info = _PlayerInfo()
            info.data['user_uid'] = user_uid
            info.rank = len(self._rank_list) + 1    # last rank
            self._player_dict[user_uid] = info
            self._rank_list.append(info)
            server_log.info("[jjc]new add user_uid=" + user_uid + ' rank=' + str(info.rank))

        if is_win:
            is_toward_front = True
            info.data['win'] += 1
            info.data['win_day'] += 1
            info.data['comb'] += 1

            if info.data['comb'] <= 1:
                honour = JJC._COMB_HONOUR_1
            elif info.data['comb'] < 10:
                honour = JJC._COMB_HONOUR_2
            else:
                honour = JJC._COMB_HONOUR_10
        else:
            is_toward_front = False
            info.data['lose'] += 1
            info.data['lose_day'] += 1
            info.data['comb'] = 0
            honour = 1

        info.data['honour'] += honour
        info.data['honour_day'] += honour

        self._update_player_in_rank(user_uid, is_toward_front)

        return info

    def handle_get_top_players(self):
        top_list = self._rank_list[:30]
        print str(top_list)
        return top_list

    def handle_find_opponent(self, user_uid):
        """ return None when not found opponent
        """

        if 'user_uid' in self._player_dict:
            info = self._player_dict[user_uid]
        else:
            # new user push to the end of rank_list
            info = _PlayerInfo()
            info.data['user_uid'] = user_uid
            info.rank = len(self._rank_list) + 1    # last rank
            self._player_dict[user_uid] = info
            self._rank_list.append(info)
            server_log.info("[jjc] new add user_uid=" + user_uid + ' rank=' + str(info.rank))

        back_count = len(self._rank_list) - info.rank
        dest_rank = JJC._make_match_seed_by_rank(info.rank, back_count, self._is_match_front)
        if dest_rank:
            oppo_user_uid = self._rank_list[dest_rank - 1].data['user_uid']
            server_log.info("[jjc] user_uid=" + user_uid + ' rank=' + str(info.rank) + 'found opponent user_uid=' +
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


if __name__ == "__main__":
    # jjc = JJC('192.168.1.250', 27017)
    conn = pymongo.MongoClient('42.62.101.24', 27017)
    jjc = JJC(conn.dota)
