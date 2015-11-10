__author__ = 'Administrator'

import pymongo
import json
from log import server_log
from collections import OrderedDict

class _PlayerInfo(object):
    def __init__(self):
        self.win = 0
        self.lose = 0
        self.honour = 0
        self.today_win = 0
        self.today_lose = 0
        self.today_honour = 0

    def load_from_dict(self, string):
        pass

    def dump_to_dict(self):
        pass

class JJC(object):
    def __init__(self, db_addr, db_port):
        self.player_dict = OrderedDict()
        conn = pymongo.MongoClient(db_addr, db_port)
        self.db = conn.dota
        self.db.jjc.ensure_index('user_uid')
        self.db.jjc.ensure_index('honour')

        # self._test_add_data()
        self._load_from_db()
        pass

    def _test_add_data(self):
        for i in range(1, 1000):
            self.db.jjc.insert({'id': i})

    def _load_from_db(self):
        cursor = None
        cursor = self.db.jjc.find()
        uset = cursor[0:self.db.jjc.count()]
        print 'ok'

    def handle_match_result(self, user_uid, is_win):
        if is_win:
            pass
        else:
            pass


if __name__ == "__main__":
    jjc = JJC('192.168.1.250', 27017)
