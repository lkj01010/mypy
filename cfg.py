# -*- coding: UTF-8 -*-


# REMOTE_LOCAL = 1
# REMOTE_HOME = 2
#
# REMOTE_WANBA = 101
# REMOTE_W2 = 102
# REMOTE_W3 = 103
# REMOTE_W4 = 104
#
# REMOTE_TEST = 201
# REMOTE_T2 = 202
# REMOTE_T3 = 203
#
# cur_remote = REMOTE_TEST
#
# SRVADDR_W = '203.195.243.33'
# SRVADDR_T = '42.62.101.24'
#
# SRV_LIST = list()
# SRV_LIST[REMOTE_WANBA] = {
#     'DB_ADDR': SRVADDR_W,
#     'DB_NAME': 'dota',
#     'TENCENT_ACCOUNT_SERVER': 'http://203.195.243.33:12000',
#     'TENCENT_ACCOUNT_SERVER_PORT': 12000,
#     'FIGURE_SERVER': 'ws://203.195.243.33:12001/figure',
#     'FIGURE_SERVER_PORT': 12001,
#     'STAT_SERVER': 'http://203.195.243.33:12011',
#     'RECORD_SERVER': 'http://203.195.243.33:12012',
#     'DB_SERVER': 'http://203.195.243.33:12013',
#     'STAT_SERVER_PORT': 12011,
#     'RECORD_SERVER_PORT': 12012,
# }
# SRV_LIST[REMOTE_W2] = {
#     'DB_ADDR': '203.195.243.33',
#     'DB_NAME': 'dota02',
#     'TENCENT_ACCOUNT_SERVER': 'http://203.195.243.33:12000',
#     'TENCENT_ACCOUNT_SERVER_PORT': 12000,
#     'FIGURE_SERVER': 'ws://203.195.243.33:12001/figure',
#     'FIGURE_SERVER_PORT': 12001,
#     'STAT_SERVER': 'http://203.195.243.33:12021',
#     'RECORD_SERVER': 'http://203.195.243.33:12022',
#     'DB_SERVER': 'http://203.195.243.33:12023',
#     'STAT_SERVER_PORT': 12021,
#     'RECORD_SERVER_PORT': 12022,
# }
# SRV_LIST[REMOTE_W3] = {
#     'DB_ADDR': '203.195.243.33',
#     'DB_NAME': 'dota03',
#     'TENCENT_ACCOUNT_SERVER': 'http://203.195.243.33:12000',
#     'TENCENT_ACCOUNT_SERVER_PORT': 12000,
#     'FIGURE_SERVER': 'ws://203.195.243.33:12001/figure',
#     'FIGURE_SERVER_PORT': 12001,
#     'STAT_SERVER': 'http://203.195.243.33:12031',
#     'RECORD_SERVER': 'http://203.195.243.33:12032',
#     'DB_SERVER': 'http://203.195.243.33:12033',
#     'STAT_SERVER_PORT': 12031,
#     'RECORD_SERVER_PORT': 12032,
# }
#
# SRV_LIST[REMOTE_TEST] = {
#     'DB_ADDR': '42.62.101.24',
#     'DB_NAME': 'dota',
#     'TENCENT_ACCOUNT_SERVER': 'http://203.195.243.33:12000',
#     'TENCENT_ACCOUNT_SERVER_PORT': 12000,
#     'FIGURE_SERVER': 'ws://42.62.101.24:12001/figure',
#     'FIGURE_SERVER_PORT': 12001,
#     'STAT_SERVER': 'http://42.62.101.24:12011',
#     'RECORD_SERVER': 'http://42.62.101.24:12012',
#     'DB_SERVER': 'http://42.62.101.24:12013',
#     'STAT_SERVER_PORT': 12011,
#     'RECORD_SERVER_PORT': 12012,
# }
# SRV_LIST[REMOTE_T2] = {
#     'DB_ADDR': '42.62.101.24',
#     'DB_NAME': 'dota02',
#     'TENCENT_ACCOUNT_SERVER': 'http://203.195.243.33:12000',
#     'TENCENT_ACCOUNT_SERVER_PORT': 12000,
#     'FIGURE_SERVER': 'ws://42.62.101.24:12001/figure',
#     'FIGURE_SERVER_PORT': 12001,
#     'STAT_SERVER': 'http://42.62.101.24:12021',
#     'RECORD_SERVER': 'http://42.62.101.24:12022',
#     'DB_SERVER': 'http://42.62.101.24:12023',
#     'STAT_SERVER_PORT': 12021,
#     'RECORD_SERVER_PORT': 12022,
# }
# SRV_LIST[REMOTE_T3] = {
#     'DB_ADDR': '42.62.101.24',
#     'DB_NAME': 'dota03',
#     'TENCENT_ACCOUNT_SERVER': 'http://203.195.243.33:12000',
#     'TENCENT_ACCOUNT_SERVER_PORT': 12000,
#     'FIGURE_SERVER': 'ws://42.62.101.24:12001/figure',
#     'FIGURE_SERVER_PORT': 12001,
#     'STAT_SERVER': 'http://42.62.101.24:12031',
#     'RECORD_SERVER': 'http://42.62.101.24:12032',
#     'DB_SERVER': 'http://42.62.101.24:12033',
#     'STAT_SERVER_PORT': 12031,
#     'RECORD_SERVER_PORT': 12032,
# }
#
# # if cur_remote == REMOTE_WANBA:
# #     DB_ADDR = '203.195.243.33'
# #     DB_NAME = 'dota'
# #     DB_SERVER = 'http://203.195.243.33:12301'
# #     RECORD_SERVER = 'http://203.195.243.33:12304'
# #     TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'
# #     STAT_SERVER = 'http://203.195.243.33:12305'
# #     FIGURE_SERVER = 'ws://203.195.243.33:12309/figure'
# #     TENCENT_ACCOUNT_SERVER_PORT = 12303
# #     RECORD_SERVER_PORT = 12304
# #     STAT_SERVER_PORT = 12305
# #     FIGURE_SERVER_PORT = 12309
# #
# # elif cur_remote == REMOTE_W2:
# #     DB_ADDR = '203.195.243.33'
# #     DB_NAME = 'dota02'
# #     DB_SERVER = 'http://203.195.243.33:12321'
# #     RECORD_SERVER = 'http://203.195.243.33:12324'
# #     TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'
# #     STAT_SERVER = 'http://203.195.243.33:12325'
# #     FIGURE_SERVER = 'ws://203.195.243.33:12329/figure'
# #     TENCENT_ACCOUNT_SERVER_PORT = 12303
# #     RECORD_SERVER_PORT = 12324
# #     STAT_SERVER_PORT = 12325
# #     FIGURE_SERVER_PORT = 12309
# #
# # elif cur_remote == REMOTE_TEST:
# #     DB_ADDR = '42.62.101.24'
# #     DB_NAME = 'dota'
# #     DB_SERVER = 'http://42.62.101.24:12310'
# #     RECORD_SERVER = 'http://42.62.101.24:12304'
# #     TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'
# #     STAT_SERVER = 'http://42.62.101.24:12305'
# #     FIGURE_SERVER = 'ws://42.62.101.24:12309/figure'
# #     TENCENT_ACCOUNT_SERVER_PORT = 12303
# #     RECORD_SERVER_PORT = 12304
# #     STAT_SERVER_PORT = 12305
# #     FIGURE_SERVER_PORT = 12309
# #
# # elif cur_remote == REMOTE_LOCAL:
# #     DB_ADDR = '42.62.101.24'
# #     # DB_ADDR = '192.168.1.250'
# #     DB_SERVER = 'http://42.62.101.24:12310'
# #     # DB_SERVER = 'http://127.0.0.1:12310'
# #     DB_NAME = 'dota'
# #     RECORD_SERVER = 'http://127.0.0.1:12304'
# #     TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'
# #     STAT_SERVER = 'http://127.0.0.1:12305'
# #     TENCENT_ACCOUNT_SERVER_PORT = 12303
# #     RECORD_SERVER_PORT = 12304
# #     STAT_SERVER_PORT = 12305
# #     FIGURE_SERVER_PORT = 12309
# #
# # elif cur_remote == REMOTE_HOME:
# #     DB_ADDR = '10.211.55.6'
# #     DB_SERVER = 'http://127.0.0.1:12310'
# #     DB_NAME = 'dota'
# #     RECORD_SERVER = 'http://127.0.0.1:12304'
# #     TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12308'
# #     STAT_SERVER = 'http://127.0.0.1:12305'
# #     TENCENT_ACCOUNT_SERVER_PORT = 12303
# #     RECORD_SERVER_PORT = 12304
# #     STAT_SERVER_PORT = 12305
# #     FIGURE_SERVER_PORT = 12309

# DB_PORT = 27017

RT_W1 = 'w1'
RT_W2 = 'w2'
RT_W3 = 'w3'

RT_T1 = 't1'
RT_T2 = 't2'
RT_T3 = 't3'

RT_4399_1 = '4399_1'
RT_4399_2 = '4399_2'

RT_1758_1 = '1758_1'
RT_1758_2 = '1758_2'

RT_WX = 'wx'

RT_1758_1T = '1758_1t'
RT_1758_2T = '1758_2t'

RT_L = 'l'

_IPs = {
    RT_L: '127.0.0.1',

    RT_W1: '203.195.243.33',
    RT_W2: '203.195.243.33',
    RT_W3: '203.195.243.33',

    RT_T1: '42.62.101.24',
    RT_T2: '42.62.101.24',
    RT_T3: '42.62.101.24',

    RT_1758_1T: '42.62.101.24',
    RT_1758_2T: '42.62.101.24',

}

_PORT_PREFIXs = {
    RT_L: 12010,

    RT_W1: 12010,
    RT_W2: 12020,
    RT_W3: 12030,

    RT_T1: 12010,
    RT_T2: 12020,
    RT_T3: 12030,


    RT_1758_1T: 13010,
    RT_1758_1T: 13020,
}

_PORT_TAILs = {
    'record': 1,
    'db': 2
}

_DBNAMEs = {
    RT_W1: 'dota',
    RT_W2: 'dota02',
    RT_W3: 'dota03',

    RT_T1: 'dota',
    RT_T2: 'dota02',
    RT_T3: 'dota03',

    RT_L: 'dota',

    RT_1758_1T: 'dota_1758_1',
    RT_1758_2T: 'dota_1758_2',
}

"""0: no 1: wanba"""
_TOKEN_CHECKs = {
    RT_L: 0,

    RT_W1: 1,
    RT_W2: 1,
    RT_W3: 1,

    RT_T1: 1,
    RT_T2: 1,
    RT_T3: 1,

    RT_1758_1T: 0,
    RT_1758_2T: 0,
}

"""0: not div, 1: div
"""
_OS_DIVs = {
    RT_L: 1,

    RT_W1: 1,
    RT_W2: 1,
    RT_W3: 1,

    RT_T1: 1,
    RT_T2: 1,
    RT_T3: 1,

    RT_1758_1T: 1,
    RT_1758_2T: 0,
}

'''正式服'''
def is_formal(rt):
    if rt == RT_W1 or rt == RT_W2 or rt == RT_W3:
        return 1
    else:
        return 0
'''玩吧'''
def is_wanba(rt):
    if rt == RT_W1 or rt == RT_W2 or rt == RT_W3 or \
            rt == RT_T1 or rt == RT_T2 or rt == RT_T3:
        return 1
    else:
        return 0

"""tecnet"""
def port_tencent():
    return 12000
def addr_tencent():
    return 'http://' + _IPs[RT_W1] + ':' + str(port_tencent())


"""stat"""
def port_stat():
    return 12001
def addr_stat(rt):
    return 'http://' + _IPs[rt] + ':' + str(port_stat())


"""figure"""
def port_figure():
    return 12002
def addr_figure(rt):
    return 'ws://' + _IPs[rt] + ':' + str(port_figure())


"""mongodb"""
def ip_mongodb(rt):
    if is_formal(rt) == 1:
        return "127.0.0.1"
    else:
        return _IPs[rt]
def port_mongodb():
    return 27017
def dbname_mongodb(rt):
    return _DBNAMEs[rt]

"""------------------"""

"""record srv"""
def port_record(rt):
    return _PORT_PREFIXs[rt] + _PORT_TAILs['record']
def addr_record(rt):
    return 'http://' + _IPs[rt] + ':' + str(port_record(rt))

"""db srv"""
def addr_db(rt):
    return 'http://' + _IPs[rt] + ':' + str(port_db(rt))
def port_db(rt):
    return _PORT_PREFIXs[rt] + _PORT_TAILs['db']

"""token check"""
def token_check(rt):
    return _TOKEN_CHECKs[rt]

"""os div"""
def os_div(rt):
    return _OS_DIVs(rt)

srvcfg = None
srvinfo = None
remote_type = ''
def setup_srvcfg(rt):
    global remote_type
    remote_type = rt
    global srvcfg
    srvcfg = {
        'ip_mongodb': ip_mongodb(rt),
        'port_mongodb': port_mongodb(),
        'dbname_mongodb': dbname_mongodb(rt),

        'addr_tencent': addr_tencent(),
        'port_tencent': port_tencent(),

        'addr_figure': addr_figure(rt),
        'port_figure': port_figure(),

        'addr_stat': addr_stat(rt),
        'port_stat': port_stat(),

        'addr_record': addr_record(rt),
        'port_record': port_record(rt),

        'addr_db': addr_db(rt),
        'port_db': port_db(rt),

        'token_check': token_check(rt),
        'os_div': os_div(rt),

        'is_formal': is_formal(rt),
        'is_wanba': is_wanba(rt),
    }

    global srvinfo
    if rt == RT_W1 or rt == RT_W2 or rt == RT_W3:
        srvinfo = {
            "list": [
                {
                    "id": RT_W1,
                    "name": "封测区",
                    "tencent": addr_tencent(),
                    "record": addr_record(RT_W1),
                    "figure": addr_figure(RT_W1)
                },

                {
                    "id": RT_W2,
                    "name": "刀塔一区(新)",
                    "tencent": addr_tencent(),
                    "record": addr_record(RT_W2),
                    "figure": addr_figure(RT_W2)
                },
            ],
            "recommend": RT_W2
        }
    elif rt == RT_T1 or rt == RT_T2 or rt == RT_T3:
        srvinfo = {
            "list": [
                {
                    "id": RT_T1,
                    "name": "刀塔测试一区",
                    "tencent": addr_tencent(),
                    "record": addr_record(RT_T1),
                    "figure": addr_figure(RT_T1)
                },
                {
                    "id": RT_T2,
                    "name": "刀塔测试二区",
                    "tencent": addr_tencent(),
                    "record": addr_record(RT_T2),
                    "figure": addr_figure(RT_T2)
                },
                {
                    "id": RT_T3,
                    "name": "刀塔测试二区",
                    "tencent": addr_tencent(),
                    "record": addr_record(RT_T3),
                    "figure": addr_figure(RT_T3)
                },
            ],
            "recommend": RT_T3
        }
    elif rt == RT_1758_1T or rt == RT_1758_2T:
        srvinfo = {
            "list": [
                {
                    "id": RT_1758_1T,
                    "name": "1758刀塔测试一区",
                    "tencent": addr_tencent(),
                    "record": addr_record(RT_1758_1T),
                    "figure": addr_figure(RT_1758_1T)
                },

                {
                    "id": RT_1758_2T,
                    "name": "1758刀塔测试二区",
                    "tencent": addr_tencent(),
                    "record": addr_record(RT_1758_2T),
                    "figure": addr_figure(RT_1758_2T)
                },
            ],
            "recommend": RT_1758_2T
        }


''' ----------------------
'''
test_users = {
            "3629E0CA4B230D4D44E692AA30B24F6D": 0,    # lkj
            "0FEFA3B77BF37C6823B0FF49509FD6F8": 0,
            "28944BB32D106957F2F0D1BE6CEDCD11": 0,
            "B1D43980E13A9C90F74F2C7405AE54A8": 0,    # eric
            "E2A3BA5A805A5B4CCD8E2BB968E60D3D": 0,
            "4E7F433E6E89C32A4BFC6528DFDE3083": 0,
        }

'''----------------------
'''




''' NOTE pymongo
1. update_one: sec param should like '$set  *****'  not a 'xx:xx' , must begin with '$', or you should use 'replace_one'
'''
''' NOTE tornado
1. tornado.web: when reply to client, 'send_error()' contain 'finish'
'''
''' NOTE python
1. OrderedDict only remember the order occur in 'init' or 'setitem'(push to the end)
'''

'''NOTE game design
1. in user data, data on srv and data send to user should all save in cache (now only data to user is save)
'''