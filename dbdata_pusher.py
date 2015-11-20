# -*- coding: UTF-8 -*-
import tornado.httpclient
from log import server_log
import json


class DBData(dict):
    def __init__(self):
        """
        touch user +1 when touched !
        """
        self.touch = 0
        self.push = 0


class DBDataPusher:
    """ cache item should be instance of DBData
    """
    def __init__(self, client, url, db_collection, cache, item_gen_callback, syn_interval):
        self._client = client
        self._url = url
        self._db_collection = db_collection
        self._cache = cache
        self._item_gen_callback = item_gen_callback
        self._syn_interval = syn_interval

    def start(self):
        time_task = tornado.ioloop.PeriodicCallback(self._push_to_db, self._syn_interval)
        time_task.start()

    def _push_to_db(self):
        data_batch = list()
        for k, v in self._cache.items():
            if v.touch >= 0:
                item = self._item_gen_callback(k, v)
                data_batch.append(item)
                v.touch = 0
                v.push += 1

        push_batch = dict()
        push_batch['collection'] = self._db_collection
        push_batch['batch'] = data_batch

        j_batch = json.JSONEncoder().encode(push_batch)
        print j_batch
        request = tornado.httpclient.HTTPRequest(self._url, method='POST', body=j_batch)
        self._client.fetch(request, callback=self._push_callback)

    def _push_callback(self, response):
        if response.body:
            pass
        else:
            server_log.error('push to [' + self._url + '] error !!!')
