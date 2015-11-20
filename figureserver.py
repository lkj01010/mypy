# -*- coding: UTF-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from log import server_log
import base64
import json

class FigureHolder:
    def __init__(self):
        self.touch = 0
        self.data = None

class FigureSocketHandler(tornado.websocket.WebSocketHandler):
    figure_cache = dict()

    def __init__(self, application, request, **kwargs):
        self._client = tornado.httpclient.AsyncHTTPClient()
        self._user_id = ''
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)

    def check_origin(self, origin):
        return True

    def on_pong(self, data):
        """Invoked when the response to a ping frame is received."""
        pass

    def on_message(self, message):
        print str(id(self)) + ' on_message'
        msg_dict = json.JSONDecoder().decode(message)
        self._user_id = msg_dict['user_id']

        # if self._user_id in FigureSocketHandler.figure_cache:
        # ------------> test
        if False:
            # ]]
            reply = dict()
            reply['user_id'] = self._user_id
            reply['data'] = FigureSocketHandler.figure_cache[self._user_id]
            reply_str = json.dumps(reply)
            self.write_message(reply_str)
            self.close()
        else:
            request = tornado.httpclient.HTTPRequest(
                msg_dict['url'],
                method='GET')
            server_log.info('fetch: ' + request.url)
            self._client.fetch(request, callback=self._cb)

    def _cb(self, respond):
        """!!!!!!!!!  data64 should attach on front: 'data:image/jpeg;base64,' etc !!!!!!!!!!
        """
        data64 = base64.b64encode(respond.body)

        FigureSocketHandler.figure_cache[self._user_id] = data64

        reply = dict()
        reply['user_id'] = self._user_id
        reply['data'] = data64
        reply_str = json.dumps(reply)

        print len(data64)
        print reply_str
        self.write_message(reply_str)
        self.close()
        # total_len = len(data)
        # start = 0
        # piece_len = 22512
        # while start <= total_len:
        #     end = start + piece_len
        #     piece = data[start:end]
        #     start = end + 1
        #
        #     reply = dict()
        #     reply['user_id'] = 'lkj'
        #     reply['len'] = len(piece)
        #     reply['data'] = piece
        #     print str(reply)
        #     self.write_message(str(reply))
        # pass


    def open(self, *args, **kwargs):
        print str(id(self)) + ' open'

    def on_close(self):
        print str(id(self)) + ' on_close'

if __name__ == '__main__':
    app = tornado.web.Application([
        ('/figure', FigureSocketHandler),
    ])
    app.listen(8200)
    tornado.ioloop.IOLoop.instance().start()
