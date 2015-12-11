# -*- coding: UTF-8 -*-

import pymongo
import cfg
import datetime

now = datetime.datetime.now()
def default_record_zone():
    return {
        "nickname": "", "figureurl": ""
    }

def default_record_jjc():
        return {
            "win": 0, "win_day": 0, "lose": 0, "lose_day": 0, "honour": 0, "honour_day": 0, "comb": 0, "combmax": 0,
            "grade": 1, "grade_got": 0, "grade_balance_month": now.month,
        }

def default_record_srv():
    return {
        'gmcard': 0, 'smcard': 0,
    }

def default_record_equip_quality():
    return [1, 1, 1, 1, 1, 1]

def default_record_equip_star():
    return [0, 0, 0, 0, 0, 0]

def default_record_zhixian_times():
    return [0, 0, 0, 0, 0, 0, ]

def default_record_equip_attr():
    return [[], [], [], [], [], []]

def default_record():
    return {
        "srv": default_record_srv(),
        "gold" : 5000+999999, "guanka" : 1, "kapailan" : 3, "v_23" : 0, "v_22" : 0, "v_21" : 0,
        "kapais" : "1-1-1-1-0-0|2-2-1-1-0-0|3-8-1-1-0-0", "v_16" : 1, "v_6" : 3, "v_7" : 15, "v_0" : 50,
        "v_1" : 50, "v_2" : 0, "v_3" : 10, "v_8" : 0, "v_14" : 1,
        "chengshi_3" : 1, "zuan" : 100, "chapter" : 1, "chengshi_1" : 1, "chengshi_2" : 1,
        "v_15" : 1, "v_12" : 1, "v_13" : 1, "v_10" : 0, "v_11" : 1, "v_-1" : 1,
        "v_24": 0, "v_25": 0, "v_31": 0, "v_41": 0,
        "day": now.day, "month": now.month, "hour": now.hour,
        "jjc" : default_record_jjc(),
        "zone" : default_record_zone(),
        'gmcardleft': 0, 'smcardleft': 0, 'v_42': 0, 'v_43': 0,
        # "role": default_record_role(),
        'r_exp': 0, 'stone': 0, 'offlinesec': 0, 'modify_time': now.strftime("%Y-%m-%d-%H-%M"),
        'r_sk': [1, 0, 0, 0],
        'r_equip_quality': default_record_equip_quality(),
        'r_equip_star': default_record_equip_star(),
        'zxtimes': default_record_zhixian_times(),
        'bone': 111110, 'flakes': 111110, 'xlstone': 111110, 'dcoin': 100000,
        'r_equip_attr': default_record_equip_attr(),
        'srv_region': cfg.srvinfo.recommend,
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

def fill_keys():
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

        if  'jjc' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc': default_record_jjc()}})
            print str(_acc.acc()) + '[db_key] : add record.jjc, user:', user_uid

        if 'v_24' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.v_24': 0}})
            print str(_acc.acc()) + '[db_key] : add record.v_24, user:', user_uid

        if 'v_25' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.v_25': 0}})
            print str(_acc.acc()) + '[db_key] : add record.v_25, user:', user_uid

        if 'v_31' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.v_31': 0}})
            print str(_acc.acc()) + '[db_key] : add record.v_31, user:', user_uid

        if 'v_41' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.v_41': 0}})
            print str(_acc.acc()) + '[db_key] : add record.v_41, user:', user_uid

        if 'grade' not in doc['record']['jjc']:
            db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc.grade': 1}})
            print str(_acc.acc()) + '[db_key] : add record.jjc.grade, user:', user_uid

        if 'grade_got' not in doc['record']['jjc']:
            db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc.grade_got': 0}})
            print str(_acc.acc()) + '[db_key] : add record.jjc.grade_got, user:', user_uid

        if 'combmax' not in doc['record']['jjc']:
            db.user.update_one({'user_uid': user_uid}, {'$set':{'record.jjc.combmax': 0}})
            print str(_acc.acc()) + '[db_key] : add record.jjc.combmax, user:', user_uid

        if 'zone' not in doc['record'] or 'nickname' not in doc['record']['zone']:
            db.user.update_one({'user_uid': user_uid}, {'$set':{'record.zone': {'nickname': '', 'figureurl': ''}}})
            print str(_acc.acc()) + '[db_key] : add record.zone, user:', user_uid

        if 'day' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.month': now.month, 'record.day': now.day,
                                                                 'record.hour': now.hour}})
            print str(_acc.acc()) + '[db_key] : add record.hour,day,month, user:', user_uid

        if 'srv' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.srv': default_record_srv(),
                                                                 'record.smcardleft': 0,
                                                                 'record.gmcardleft:': 0,
                                                                 'record.v_42': 0,
                                                                 'record.v_43': 0}})
            print str(_acc.acc()) + '[db_key] : add record.srv, user:', user_uid

        if 'role' in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$unset': {'record.role': True}})
            print str(_acc.acc()) + '[db_key] : del record.role:', user_uid

        if 'stone' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.stone': 0, 'record.r_exp': 0}})
            print str(_acc.acc()) + '[db_key] : add record.r_exp and stone:', user_uid

        if 'offlinesec' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.offlinesec': 0}})
            print str(_acc.acc()) + '[db_key] : add record.offlinesec:', user_uid

        if 'modify_time' not in doc['record']:
        # if True:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.modify_time': now.strftime("%Y-%m-%d-%H-%M")}})
            print str(_acc.acc()) + '[db_key] : add record.modify_time:', user_uid

        if 'r_sk' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.r_sk': [1, 0, 0, 0]}})
            print str(_acc.acc()) + '[db_key] : add record.r_sk:', user_uid

        if 'r_equip_quality' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.r_equip_quality': default_record_equip_quality()}})
            print str(_acc.acc()) + '[db_key] : add record.r_equip_quality:', user_uid

        if 'r_equip_quality' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.r_equip_quality': default_record_equip_quality()}})
            print str(_acc.acc()) + '[db_key] : add record.r_equip_quality:', user_uid

        if 'r_equip_star' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.r_equip_star': default_record_equip_star()}})
            print str(_acc.acc()) + '[db_key] : add record.r_equip_star:', user_uid

        if 'bone' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.bone': 0}})
            print str(_acc.acc()) + '[db_key] : add record.bone:', user_uid

        if 'flakes' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.flakes': 0}})
            print str(_acc.acc()) + '[db_key] : add record.flakes:', user_uid

        if 'xlstone' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.xlstone': 0}})
            print str(_acc.acc()) + '[db_key] : add record.xlstone:', user_uid

        if 'dcoin' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.dcoin': 0}})
            print str(_acc.acc()) + '[db_key] : add record.dcoin:', user_uid

        if 'r_equip_attr' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.r_equip_attr': default_record_equip_attr()}})
            print str(_acc.acc()) + '[db_key] : add record.r_equip_attr:', user_uid

        if 'srv_region' not in doc['record']:
            db.user.update_one({'user_uid': user_uid}, {'$set': {'record.srv_region': 1}})
            print str(_acc.acc()) + '[db_key] : add record.srv_region:', user_uid

    print '[db_key] key filling finished.'
