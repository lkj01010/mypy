# -*- coding: UTF-8 -*-
import pymongo
import random
import time

import tornado.options

import datetime

from tornado.options import define, options
define("opt", default="add", help="add", type=str)

# var = [[None for _ in range(10)] for _ in range(10)]
#
# var2 = [1 for _ in range(10)]
#
# for i, x in enumerate([1,2,3]):
#     print x
#
# for k, _ in enumerate(var):
#     print k
#
# A, B = ['a', 'b']
#
# C = 'abbccdef'
# D = b"zzz".join(C)
#
# TEST_COUNT = 1000


class Record(object):
    def __init__(self):
        self._conn = None
        self.db = None
        pass

    def run(self):
        self._conn = pymongo.MongoClient("10.211.55.6", 27017)
        # self._conn = pymongo.MongoClient("192.168.1.250", 27017)
        self.db = self._conn.dota
        pass

    def add_batch_record(self):

        for idx in range(1, TEST_COUNT):
            r1 = random.uniform(1, 100)
            r2 = random.uniform(1, 100)
            r3 = random.uniform(1, 100)
            r4 = random.uniform(1, 100)
            string = {'idx': idx, 'k1': r1, 'k2': r2, 'k3': r3, 'k4': r4}
            self.db.user.insert_one(string)

    def drop(self):
        self.db.user.drop()

    def single_update(self):
        for idx in xrange(1, TEST_COUNT):
            self.db.user.update({'idx': idx}, {'$set': {'k1': idx}}, True, True)

    def multi_update(self):
        for idx in xrange(1, TEST_COUNT):
            self.db.user.update({'idx': idx}, {'$set': {'k1': idx, 'k2': idx, 'k3': idx, 'k4': idx,
                                                        'k5': idx, 'k6': idx, 'k7': idx, 'k8': idx,
                                                        'k15': idx, 'k16': idx, 'k17': idx, 'k18': idx,
                                                        'k25': idx, 'k26': idx, 'k27': idx, 'k28': idx,
                                                        'k35': 'foofoo', 'k36': 'foofoo', 'k37': 'foofoo', 'k38': 'foofoo',
                                                        'k45': 'foofoo', 'k46': 'foofoo', 'k47': 'foofoo', 'k48': 'foofoo',
                                                        } }, True, True)

    def test_random_read(self):
        pass

    def test_random_write(self):
        pass

    def add_record(self):
        pass

import hashlib
import uuid
import urllib
import json
import urlparse

def cut_kapais(strbefore):
    cnt = 0
    i = 0
    for c in strbefore:
        if c == '|':
            cnt += 1
            if cnt > 60:
                break
        i += 1
    strafter = strbefore[0:i]
    return strafter

if __name__ == "__main__":
    if not None:
        pass

    reply_dict = dict()
    reply_dict['ok'] = True
    jstring = json.dumps(reply_dict)

    strbefore = "16-4-4-31-382-1|21-103-2-25-140-1|22-102-2-16-50-1|45-5-4-36-210-1|49-101-4-30-970-1|51-104-2-36-90-1|53-104-2-1-0-1|61-3-2-1-0-1|116-9-2-1-0-1|117-9-1-1-0-0|118-4-1-1-0-0|119-1-1-1-0-0|120-5-1-1-0-0|121-9-1-1-0-0|122-8-1-1-0-0|123-4-1-1-0-0|124-3-1-1-0-0|125-10-1-1-0-0|126-10-1-1-0-0|127-8-1-1-0-0|128-6-1-1-0-0|129-7-1-1-0-0|130-6-1-1-0-0|131-2-1-1-0-0|132-10-1-1-0-0|133-8-1-1-0-0|134-7-1-1-0-0|135-5-1-1-0-0|136-5-1-1-0-0|137-9-1-1-0-0|138-8-1-1-0-0|139-10-1-1-0-0|140-6-1-1-0-0|141-7-1-1-0-0|142-2-1-1-0-0|143-6-1-1-0-0|144-6-1-1-0-0|145-7-1-1-0-0|146-10-1-1-0-0|147-3-1-1-0-0|148-8-1-1-0-0|149-5-1-1-0-0|150-5-1-1-0-0|151-1-1-1-0-0|152-2-1-1-0-0|153-5-1-1-0-0|154-7-1-1-0-0|155-2-1-1-0-0|156-4-1-1-0-0|157-6-1-1-0-0|158-10-1-1-0-0|159-1-1-1-0-0|160-7-1-1-0-0|161-1-1-1-0-0|162-2-1-1-0-0|163-1-1-1-0-0|164-10-1-1-0-0|165-4-1-1-0-0|166-2-1-1-0-0|167-9-1-1-0-0|168-3-1-1-0-0|169-5-1-1-0-0|170-2-1-1-0-0|171-7-1-1-0-0|172-3-1-1-0-0|173-1-1-1-0-0|174-10-1-1-0-0|175-6-1-1-0-0|176-5-1-1-0-0|177-4-1-1-0-0|178-3-1-1-0-0|179-8-1-1-0-0|180-10-1-1-0-0|181-7-1-1-0-0|182-9-1-1-0-0|183-4-1-1-0-0|184-6-1-1-0-0|185-3-1-1-0-0|186-9-1-1-0-0|187-2-1-1-0-0|188-9-1-1-0-0|189-7-1-1-0-0|190-4-1-1-0-0|191-4-1-1-0-0|192-4-1-1-0-0|193-9-1-1-0-0|194-10-1-1-0-0|195-9-1-1-0-0|196-3-1-1-0-0|197-8-1-1-0-0|198-5-1-1-0-0|199-6-1-1-0-0|200-6-1-1-0-0|201-8-1-1-0-0|202-8-1-1-0-0|206-5-1-1-0-0|207-9-1-1-0-0|208-9-1-1-0-0|209-8-1-1-0-0|211-2-1-1-0-0|212-7-1-1-0-0|213-4-1-1-0-0|214-9-1-1-0-0|215-3-1-1-0-0|216-5-1-1-0-0|217-7-1-1-0-0|219-8-1-1-0-0|220-3-1-1-0-0|221-7-1-1-0-0|222-8-1-1-0-0|223-9-1-1-0-0|224-3-1-1-0-0|225-3-1-1-0-0|226-6-1-1-0-0|227-7-1-1-0-0|228-8-1-1-0-0|229-4-1-1-0-0|230-8-1-1-0-0|231-4-1-1-0-0|232-5-1-1-0-0|233-2-1-1-0-0|234-10-1-1-0-0|235-5-1-1-0-0|237-10-1-1-0-0|238-10-1-1-0-0|239-7-1-1-0-0|241-5-1-1-0-0|242-6-1-1-0-0|243-9-1-1-0-0|244-2-1-1-0-0|245-4-1-1-0-0|246-8-1-1-0-0"
    cnt = 0
    i = 0
    pos = -1
    for c in strbefore:
        if c == '|':
            cnt += 1
            if cnt > 60:
                pos = i
                break
        i += 1
    strafter = strbefore[0:i]
    print strafter

    print cut_kapais(strbefore)

    jfiejf = list()
    jfiejf.append('xxx')

    params = urlparse.parse_qs('appAccount=TrIL0001450836525175IpeJx477jd3r&appCode=tiandota&appOrder=e72cb41aad3811e596bdfa163e3bd9e1&cashFee=1&openCode=tiandota&orderNo=20151228155924453oQZ5bW0JKCogtGr&otherInfo=%7B%22pay_code%22%3A1%2C%22os%22%3A32%2C%22channel%22%3A%22acsp_1758_t%22%2C%22region%22%3A1%7D&payResult=1&payTime=20151228160059&sign=214861acc9cd8def53c6a78eaee70565&totalFee=1')
    otherinfo = json.JSONDecoder().decode(params['otherInfo'][0])
    orderid = str(uuid.uuid1())

    print orderid.replace('-', '')
    print len(orderid.replace('-', ''))
    orderid = str(uuid.uuid4())
    print orderid

    md5 = hashlib.md5()
    sss1 = md5.update('你是谁')
    print md5.hexdigest()
    sss2 = md5.update('xxx')
    print md5.hexdigest()

    jfei = u'你是是是是'
    print type(jfei)

    jxxj = ["xx", "yy", "zz"]
    for k in enumerate(jxxj):
        print k
    for v in jxxj:
        print v

    testset = set()
    testset.add('谁是你的')

    todaystr = datetime.datetime.today().strftime('%Y-%m-%d')
    today = datetime.date.today()
    todaystring = today.strftime('%Y-%m-%d')
    print datetime.datetime.now()

    equip = list()

    for i in range(1, 6):
        item = dict()
        item['qua'] = 1
        item['gem'] = ['', '', '', '', '', '']

        equip.append(item)

    deadline = datetime.datetime.now() + datetime.timedelta(days=30)
    print deadline
    deadline2 = deadline.replace(hour=0, minute=0, second=0)
    print deadline2
    x = deadline - deadline2
    if deadline > deadline2:
        print x.days

    strdd = deadline.strftime("%Y-%m-%d-%H-%M")
    xxx = datetime.datetime.strptime(strdd, "%Y-%m-%d-%H-%M")
    print 10 % 4

    xaa = 10
    if xaa % 2 == 0:
        print 'ok'

    l = [11,21,31,41,51,61,71,81]
    for k in enumerate(l[2:6]):
        print k
        print k[1]

    now = datetime.datetime.now()
    d = now.day
    day = now.date()

    tt = datetime.time(21,0,0)


    sss = '12345'
    sss = sss[:-1]

    zz1 = {'1':1}
    zz2 = {'2':1}
    zz3 = {'3':1}
    dict = {'1':zz1, '2':zz2, '3':zz3}

    del zz1


    import json
    collection_path = list()
    collection_path.append('stat')
    collection_path.append('realtime')

    stat_dict = dict()
    stat_dict['collection'] = collection_path
    stat_dict['key'] = {}

    j_stat = json.JSONEncoder().encode(stat_dict)

    logstr = ''
    for i in range(1,3):
        logstr += str(i)
    print logstr + '123'

    aa = {'a1': 1, 'b1': 2, 'c1': 3}
    for k, v in aa.items():
        if v == 2:
            del aa[k]

    aa.clear()

    if 'a1' in aa:
        print 'a1 in aa'

    if 'a1' in aa.keys():
        print 'a1 in aakeys'

    str1 = 'xxxxx'
    str2 = u'xxxxx'
    if str1 == str2:
        print str1,str2

    bset = set()
    bset.add('x1')
    if 'x1' in bset:
        print 'ok'
    bset.add('x1')
    print str(len(bset))

    print str(len(aa))

    time_str = time.mktime(time.localtime())

    i = iter("abcd")
    print i.next()
    print i.next()
    print i.next()

    tornado.options.parse_command_line()
    r = Record()
    r.run()
    start_time = time.time()

    # r.single_update()
    r.multi_update()

    consume = time.time() - start_time
    print 'use time: ' + str(consume)
    r.db.user.remove()

    # if options.opt == 'del':
    #     r.drop()
    # else:
    # r.add_batch_record()



