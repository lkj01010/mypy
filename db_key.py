# -*- coding: UTF-8 -*-

import pymongo
import cfg
import datetime

def default_record_zone():
    return {
        "nickname": "", "figureurl": ""
    }

def default_record_jjc():
        return {
            "win": 0, "win_day": 0, "lose": 0, "lose_day": 0, "honour": 0, "honour_day": 0, "comb": 0, "grade": 1,
            "grade_got": 0, "grade_balance_month": now.month,
        }

def default_record():
    now = datetime.datetime.now()
    return {
        "gold" : 5000, "guanka" : 1, "kapailan" : 3, "v_23" : 0, "v_22" : 0, "v_21" : 0,
        "kapais" : "1-1-1-1-0-0|2-2-1-1-0-0|3-8-1-1-0-0", "v_16" : 1, "v_6" : 3, "v_7" : 15, "v_0" : 50,
        "v_1" : 50, "v_2" : 0, "v_3" : 10, "v_8" : 0, "v_14" : 1,
        "chengshi_3" : 1, "zuan" : 100, "chapter" : 1, "chengshi_1" : 1, "chengshi_2" : 1,
        "v_15" : 1, "v_12" : 1, "v_13" : 1, "v_10" : 0, "v_11" : 1, "v_-1" : 1,
        "day": now.day, "month": now.month, "hour": now.hour,
        "jjc" : default_record_jjc(),
        "zone" : default_record_zone(),
    }

conn = pymongo.MongoClient(cfg.DB_ADDR, cfg.DB_PORT)
db = conn.dota
cursor = db.user.find({}, projection={'_id': False})

class _Acc:
    _u_count = 0

    def __init__(self):
        pass

    @staticmethod
    def acc():
        _Acc._u_count += 1
        return _Acc._u_count

_acc = _Acc()
now = datetime.datetime.now()
print '[db_key] do key filling ...'
for doc in cursor:
    if 'user_uid' not in doc:
        print str(_acc.acc()) + '[db_key] error: user_uid not in'
        db.user.delete_one(doc)    # doc itself is a filter !!!
        continue
    user_uid = doc['user_uid']
    if 'record' not in doc:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record': default_record()}})
        print str(_acc.acc()) + '[db_key] : add record, user:', user_uid
        continue

    if  'jjc' not in doc['record']:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc': default_record_jjc()}})
        print str(_acc.acc()) + '[db_key] : add record.jjc, user:', user_uid
        continue

    if 'grade' not in doc['record']['jjc']:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc.grade': 1}})
        print str(_acc.acc()) + '[db_key] : add record.jjc.grade, user:', user_uid
        continue

    if 'grade_got' not in doc['record']['jjc']:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc.grade_got': 0}})
        print str(_acc.acc()) + '[db_key] : add record.jjc.grade_got, user:', user_uid
        continue

    if 'zone' not in doc['record'] or 'nickname' not in doc['record']['zone']:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record.zone': {'nickname': '', 'figureurl': ''}}})
        print str(_acc.acc()) + '[db_key] : add record.zone, user:', user_uid

    if 'day' not in doc['record']:
        db.user.update_one({'user_uid': user_uid}, {'$set': {'record.month': now.month, 'record.day': now.day,
                                                             'record.hour': now.hour}})
        print str(_acc.acc()) + '[db_key] : add record.hour,day,month, user:', user_uid

print '[db_key] key filling finished.'
