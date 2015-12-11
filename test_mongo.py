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


if __name__ == "__main__":
    if not None:
        pass

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



