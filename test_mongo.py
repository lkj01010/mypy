import pymongo
import random
import time

import tornado.options

from tornado.options import define, options
define("opt", default="add", help="add", type=str)

var = [[None for _ in range(10)] for _ in range(10)]

var2 = [1 for _ in range(10)]

for i, x in enumerate([1,2,3]):
    print x

for k, _ in enumerate(var):
    print k

A, B = ['a', 'b']

C = 'abbccdef'
D = b"zzz".join(C)

TEST_COUNT = 1000


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

    aa = {'a1': 1, 'b1': 2, 'c1': 3}
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



