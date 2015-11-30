# -*- coding: UTF-8 -*-
REMOTE_WANBA = 0
REMOTE_TEST = 1
REMOTE_LOCAL = 2
REMOTE_HOME = 3

cur_remote = REMOTE_WANBA

if cur_remote == REMOTE_WANBA:
    DB_ADDR = '127.0.0.1'
    DB_SERVER = 'http://127.0.0.1:12310'
    RECORD_SERVER = 'http://127.0.0.1:12304'
    TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'
    TENCENT_ACCOUNT_SERVER_PORT = 12303

elif cur_remote == REMOTE_TEST:
    DB_ADDR = '127.0.0.1'
    DB_SERVER = 'http://127.0.0.1:12310'
    RECORD_SERVER = 'http://127.0.0.1:12304'
    TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'
    TENCENT_ACCOUNT_SERVER_PORT = 12303

elif cur_remote == REMOTE_LOCAL:
    DB_ADDR = '42.62.101.24'
    # DB_ADDR = '192.168.1.250'
    # DB_SERVER = 'http://42.62.101.24:12310'
    DB_SERVER = 'http://127.0.0.1:12310'
    RECORD_SERVER = 'http://127.0.0.1:12304'
    TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'
    TENCENT_ACCOUNT_SERVER_PORT = 12303

elif cur_remote == REMOTE_HOME:
    DB_ADDR = '10.211.55.6'
    DB_SERVER = 'http://127.0.0.1:12310'
    RECORD_SERVER = 'http://127.0.0.1:12304'
    TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12308'
    TENCENT_ACCOUNT_SERVER_PORT = 12308

DB_PORT = 27017
RECORD_SERVER_PORT = 12304
STAT_SERVER_PORT = 12305


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



''' NOTE pymongo
1. update_one: sec param should like '$set  *****'  not a 'xx:xx' , must begin with '$', or you should use 'replace_one'
'''
''' NOTE tornado
1. tornado.web: when reply to client, 'send_error()' contain 'finish'
'''
''' NOTE python
1. OrderedDict only remember the order occur in 'init' or 'setitem'(push to the end)
'''