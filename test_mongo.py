import pymongo
import random

class record(object):
    def __init__(self):
        pass

    def run(self):
        self.conn = pymongo.MongoClient("10.211.55.6", 27017)
        pass

    def add_batch_record(self):
        r1 = random.uniform(1, 100)
        r2 = random.uniform(1, 100)
        r3 = random.uniform(1, 100)
        r4 = random.uniform(1, 100)
        for idx in range(1, 1000):
            str = {'k1':r1, 'k2':r2, 'k3':r3, 'k4':r4}
            self.conn.insert_one(str)


    def remove_record_all(self):
        self.conn.remove

    def add_record(self):
        pass


if __name__ == "__main__":
    r = record()
