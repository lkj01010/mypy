import pymongo
import json

class Record(object):
    def __init__(self):
        conn = pymongo.MongoClient("192.168.1.250", 27017)
        self.db = conn['dota']
        # for index in self.db.user.list_indexes():
        #     print(index)
        # self.db.user.drop_index('_id') #  drop '_id' is invalid
        self.db.user.create_index('user_id')
        pass

    @staticmethod
    def default_record():
        record = {
            '-1': 0,

            "0": 50,    # music
            "1": 50,    # effect

            "3": -1,    # daily reward
            "6": 3,     # liuxinghuoyu
            "7": 15,    # card bag space

            "kapailan": 3,
            "chapter": 1,
            "guanka": 1,

            "chengshiLv_1": 1,
            "chengshiLv_2": 1,
            "chengshiLv_3": 1,

            "kapai_1": 1,
            "kapai_2": 1,
            "kapai_8": 1,

            "gold": 5000,

            "11": 1,
            "12": 1,
            "13": 1,
            "14": 1,
            "15": 1,
            "16": 1
        }
        return record

    def get_record(self, user_id):
        find_ret = self.db.user.find_one({'user_id': user_id})
        if find_ret:
            del find_ret['_id']
            reply_dict = dict((key.encode('ascii'), value) for key, value in find_ret['record'].items())
            return reply_dict
        else:
            record_doc = dict()
            record_doc['user_id'] = user_id
            record_doc['record'] = Record.default_record()
            self.db.user.insert(record_doc)

            reply_dict = Record.default_record()
            return reply_dict

    def commit_record_item(self, user_id, info):
        j_info = json.JSONEncoder().encode(info)
        self.db.update({'user_id': user_id}, j_info, True)

