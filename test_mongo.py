import pymongo
import random

import tornado.options

from tornado.options import define, options
define("opt", default="add", help="add", type=str)

var = [[None for _ in range(10)] for _ in range(10)]

var2 = [1 for _ in range(10)]

for i, x in enumerate([1,2,3]):
    print x

for k,_ in enumerate(var):
    print k

A,B = ['a', 'b']

C = 'abbccdef'
D = b"zzz".join(C)

class record(object):
    def __init__(self):
        pass

    def run(self):
        self._conn = pymongo.MongoClient("10.211.55.6", 27017)
        self._db = self._conn.dota
        pass

    def add_batch_record(self):

        for idx in range(1, 1000):
            r1 = random.uniform(1, 100)
            r2 = random.uniform(1, 100)
            r3 = random.uniform(1, 100)
            r4 = random.uniform(1, 100)
            str = {'k1':r1, 'k2':r2, 'k3':r3, 'k4':r4}
            self._db.user.insert_one(str)


    def drop(self):
        self._db.user.drop()

    def single_update(self):
        for idx in range(1, 1000):
            pass

    def add_record(self):
        pass


if __name__ == "__main__":
    if not None:
        pass

    tornado.options.parse_command_line()
    r = record()
    r.run()
    r._db.user.remove()

    # if options.opt == 'del':
    #     r.drop()
    # else:
    # r.add_batch_record()



