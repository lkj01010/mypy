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
    clients = set()
    figure_cache = dict()

    def __init__(self, application, request, **kwargs):
        self._client = tornado.httpclient.AsyncHTTPClient()
        tornado.websocket.WebSocketHandler.__init__(self, application, request, **kwargs)

    def check_origin(self, origin):
        return True

    @staticmethod
    def send_to_all(message):
        for c in FigureSocketHandler.clients:
            c.write_message(message)

    def on_pong(self, data):
        """Invoked when the response to a ping frame is received."""
        pass

    def on_message(self, message):
        request = tornado.httpclient.HTTPRequest(
            'http://thirdapp3.qlogo.cn/qzopenapp/d8219673598dbd6f634b7a98010859c7e9d7b24659e5a442c94004fd58149411/50',
            method='GET')
        server_log.info('new active url: ' + request.url)
        self._client.fetch(request, callback=self._cb)

    def _cb(self, respond):
        data64 = base64.b64encode(respond.body)
        data64 += data64
        data64 += data64
        data64 += data64
        data64 += data64
        data64 += data64
        data64 += data64
        data64 += data64
        data64 += data64
        reply = dict()
        reply['user_id'] = 'lkj'
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
        FigureSocketHandler.send_to_all(str(id(self)) + ' has joined')
        FigureSocketHandler.clients.add(self)

    def on_close(self):
        FigureSocketHandler.clients.remove(self)
        FigureSocketHandler.send_to_all(str(id(self)) + ' has left')

if __name__ == '__main__':
    app = tornado.web.Application([
        ('/figure', FigureSocketHandler),
    ])
    app.listen(8200)
    tornado.ioloop.IOLoop.instance().start()
