# -*- coding: UTF-8 -*-
REMOTE_WANBA = 0
REMOTE_TEST = 1
REMOTE_LOCAL = 2

cur_remote = REMOTE_LOCAL

if cur_remote == REMOTE_WANBA:
    DB_ADDR = '127.0.0.1'
    DB_SERVER = 'http://127.0.0.1:12310'
    RECORD_SERVER = 'http://127.0.0.1:12304'
elif cur_remote == REMOTE_TEST:
    DB_ADDR = '127.0.0.1'
    DB_SERVER = 'http://127.0.0.1:12310'
    RECORD_SERVER = 'http://127.0.0.1:12304'
elif cur_remote == REMOTE_LOCAL:   # LOCAL
    # DB_ADDR = '42.62.101.24'
    DB_ADDR = '192.168.1.250'
    # DB_SERVER = 'http://42.62.101.24:12310'
    DB_SERVER = 'http://127.0.0.1:12310'
    RECORD_SERVER = 'http://127.0.0.1:12304'

DB_PORT = 27017
RECORD_SERVER_PORT = 12304
TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'

''' NOTE pymongo
1. update_one: sec param should like '$set  *****'  not a 'xx:xx' , must begin with '$', or you should use 'replace_one'
'''
''' NOTE tornado
1. tornado.web: when reply to client, 'send_error()' contain 'finish'
'''
''' NOTE python
1. OrderedDict only remember the order occur in 'init' or 'setitem'(push to the end)
'''