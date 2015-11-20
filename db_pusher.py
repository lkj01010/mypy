# -*- coding: UTF-8 -*-
import tornado.httpclient
from log import server_log
import json


class DataHolder:
    def __init__(self, data):
        self.data = data
        self.touch = 0
        self.push = 0
        self.active = False

class DBPusher:
    """ cache item should be instance of _DataHolder
    """
    def __init__(self, client, url, cache, syn_interval, clean_interval):
        self._client = client
        self._url = url
        self._cache = cache
        self._syn_interval = syn_interval
        self._clean_interval = clean_interval

    def start(self):
        time_task = tornado.ioloop.PeriodicCallback(self._push_to_db, self._syn_interval)
        time_task.start()
        time_task2 = tornado.ioloop.PeriodicCallback(self._clean_inactive,
                                                     self._clean_interval)
        time_task2.start()

    def _push_to_db(self):
        batch = dict()
        for k, v in self._cache.items():
            if v.touch > 0:
                batch[k] = v.data
                v.touch = 0
                v.active = True
                """ after 50 cleanup circle,v will release from cache """
                if v.push < 2:  # test
                    v.push += 1

        # [[ test for log
        logstr = str()
        for k in self._cache:
            logstr += '\nkey=' + k + ', touch=' + str(self._cache[k].touch) + ', push=' + str(self._cache[k].push)
        server_log.info('[' + self._url + '] ' + logstr)
        # ]]

        j_batch = json.JSONEncoder().encode(batch)
        request = tornado.httpclient.HTTPRequest(self._url, method='POST', body=j_batch)
        self._client.fetch(request, callback=self._push_callback)
        pass

    def _push_callback(self, response):
        if response.body:
            pass
        else:
            server_log.error('push to [' + self._url + '] error !!!')

    def _clean_inactive(self):
        for k, v in self._cache.items():
            if v.push <= 0:
                del self._cache[k]
            else:
                self._cache[k].push -= 1

        # [[ test for log
        logstr = str()
        for k in self._cache:
            logstr += '\nkey=' + k + ', touch=' + str(self._cache[k].touch) + ', push=' + str(self._cache[k].push)
        server_log.info('[push inactive]' + logstr)
        # ]]