IS_REMOTE = 0

RECORD_SERVER_PORT = 12304
TENCENT_ACCOUNT_SERVER = 'http://203.195.243.33:12303'


DB_SERVER = 'http://127.0.0.1:12310'
# DB_SERVER = 'http://192.168.1.250:12310'
# DB_SERVER = 'http://42.62.101.24:12310'
RECORD_SERVER = 'http://127.0.0.1:12304'


''' NOTE pymongo
1. update_one: sec param should like '$set  *****'  not a 'xx:xx' , must begin with '$', or you should use 'replace_one'




'''