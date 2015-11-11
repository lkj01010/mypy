# -*- coding: UTF-8 -*-

import pymongo
import json
from log import server_log
from collections import OrderedDict
import random

class _PlayerInfo(object):
    def __init__(self, data):
        # self.win = 0
        # self.lose = 0
        # self.honour = 0
        # self.today_win = 0
        # self.today_lose = 0
        # self.today_honour = 0
        #
        # self.data = dict()
        # self.data['win'] = 0
        # self.data['lose'] = 0
        # self.data['honour'] = 0
        # self.data['win_day'] = 0
        # self.data['lose_day'] = 0
        # self.data['honour_day'] = 0
        # self.data['day'] = 0
        self.data = None
        self.ranking = 10000000

    def load_from_dict(self, string):
        pass

    def dump_to_dict(self):
        pass

class JJC(object):

    _COMB_HONOUR_1 = 10
    _COMB_HONOUR_2 = 20
    _COMB_HONOUR_10 = 30

    def __init__(self, db):

        self.db = db

        # why OrderedDict not support 'reverse=True'?
        """why?"""
        self._honour_dict = OrderedDict(sorted(dict(), key=lambda t: t[0]))
        # save player by user_uid
        self._player_dict = dict()

        self._test_add_data()
        self._load_from_db()
        pass

    def _test_add_data(self):
        for i in range(1, 1000):
            self.db.jjc.insert({'user_uid': i, 'honour': random.randint(0, 1000)})

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
        for doc in cursor:
            info = _PlayerInfo(doc)
            if 'honour' in doc:
                self._honour_dict[doc['honour']] = info
                self._player_dict[doc['user_uid']] = info
                print str(doc)

        ranking = 1
        for k in self._honour_dict:
            print str(k), str(self._honour_dict[k])

        i = iter(self._honour_dict)
        while i:
            print str(i.next())

        pass

    def handle_match_result(self, user_uid, is_win):
        if 'user_uid' in self._player_dict:
            info = self._player_dict[user_uid]
        else:
            info = dict()

        if is_win:
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
            info.data['lose'] += 1
            info.data['lose_day'] += 1
            info.data['comb'] = 0
            honour = 1

        info.data['honour'] += honour
        info.data['honour_day'] += honour

        return info


if __name__ == "__main__":
    # jjc = JJC('192.168.1.250', 27017)
    conn = pymongo.MongoClient('42.62.101.24', 27017)
    jjc = JJC(conn.dota)
