# -*- coding: UTF-8 -*-

import pymongo
import cfg

def default_record_jjc():
    return {
        "win": 0, "win_day": 0, "lose": 0, "lose_day": 0, "honour": 0, "honour_day": 0, "comb": 0, "grade": 1,
        "grade_got": 0
    }

def default_record():
    return {
        "gold" : 5000, "guanka" : 1, "kapailan" : 3, "v_23" : 0, "v_22" : 0, "v_21" : 0,
        "kapais" : "1-1-1-1-0-0|2-2-1-1-0-0|3-8-1-1-0-0", "v_16" : 1, "v_6" : 3, "v_7" : 15, "v_0" : 50,
        "v_1" : 50, "v_2" : 0, "v_3" : 10, "v_8" : 0, "v_14" : 1,
        "chengshi_3" : 1, "zuan" : 100, "chapter" : 1, "chengshi_1" : 1, "chengshi_2" : 1,
        "v_15" : 1, "v_12" : 1, "v_13" : 1, "v_10" : 0, "v_11" : 1, "v_-1" : 1,
        "jjc" : default_record_jjc(),
    }

conn = pymongo.MongoClient(cfg.DB_ADDR, cfg.DB_PORT)
db = conn.dota
cursor = db.user.find({}, projection={'_id': False})
for doc in cursor:
    if 'user_uid' not in doc:
        print '[db_key] error: user_uid not in'
        db.user.delete_one(doc)    # doc itself is a filter !!!
        continue
    user_uid = doc['user_uid']
    if 'record' not in doc:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record': default_record()}})
        print '[db_key] : add record, user:', user_uid
        continue

    if  'jjc' not in doc['record']:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc': default_record_jjc()}})
        print '[db_key] : add record.jjc, user:', user_uid
        continue

    if 'grade' not in doc['record']['jjc']:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc.grade': 1}})
        print '[db_key] : add record.jjc.grade, user:', user_uid
        continue

    if 'grade_got' not in doc['record']['jjc']:
        db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc.grade_got': 0}})
        print '[db_key] : add record.jjc.grade_got, user:', user_uid
        continue


