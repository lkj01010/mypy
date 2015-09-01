import pymongo

class Record(object):
    def __init__(self):
        conn = pymongo.MongoClient("192.168.1.250", 27017)
        self.db = conn['dota']
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
        replay_dict = dict()
        replay_dict['ret_code'] = 0

        find_ret = self.db.user.find_one({'id': user_id})
        if find_ret:
            del find_ret['_id']
            replay_dict['ret_code'] = 1
            replay_dict['record'] = find_ret
            return str(replay_dict)
        else:
            return str(replay_dict)

    def commit_record_item(self):

        pass

