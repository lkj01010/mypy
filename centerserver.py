# -*- coding: UTF-8 -*-

import cfg
import tornado.httpserver
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web
import json

import pymongo
import uuid
import hashlib
import datetime
import urlparse
from copy import deepcopy

from log import server_log

from tornado.options import define, options

define("rt", default='', help="reomote type", type=str)

_APP_KEY = 'EjWIvZT84jrLgvBdZRIcNnG5fOCIDD9Y'

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/client", ClientReqHandler),
            (r"/acsp/paycb", AcspPayCbHandler),
        ]
        conn = pymongo.MongoClient(cfg.srvcfg['ip_mongodb'], cfg.srvcfg['port_mongodb'])
        dbname = cfg.srvcfg['comdbname_mongodb']
        self.db = conn[dbname]
        self.db.bill.going.create_index('orderid')
        self.db.bill.user.create_index('orderid')
        server_log.info('center server start on port: ' + str(cfg.srvcfg['port_center']))

        '''用户支付成功但是没有领取道具的账单'''
        self.user_bills_going = dict()
        self._load_user_bills_going()

        tornado.web.Application.__init__(self, handlers, debug=False)

    def _load_user_bills_going(self):
        if cfg.srvcfg['channel'] == 2:
            cursor = self.db.bill.going.find({}, projection={'_id': False})
            for doc in cursor:
                self.user_bills_going[doc['user_uid']] = doc['bills']
                server_log.info('load userbill:' + str(doc))

class ClientReqHandler(tornado.web.RequestHandler):
    def get(self):
        user_uid = cfg.format_user_uid(self.get_argument('user_id'), self.get_argument('user_pf'))
        server_log.info('ClientReqHandler, format_user_uid: opencode=' + self.get_argument('user_id') + ', os=' + self.get_argument('user_pf'))

        req = self.get_argument('body').encode('utf8')

        req_dict = json.JSONDecoder().decode(req)
        server_log.info('ClientReq body=' + req)

        cmd = req_dict['cmd']
        if 'body' in req_dict:
            body = req_dict['body']
        else:
            body = dict()

        if cmd == 'query_order':
            reply_dict = self._handle_query_order(user_uid, body)
        elif cmd == 'query_pay_ret':
            reply_dict = self._handle_query_pay_ret(user_uid, body)
        else:
            raise Exception

        reply = str(self.get_argument('callback')) + '(' + json.dumps(reply_dict) + ')'
        server_log.info('ClientReq ret=' + json.JSONEncoder().encode(reply))
        self.write(reply)
        pass

    def _handle_query_order(self, user_uid, body):
        orderid = str(uuid.uuid1()).replace('-', '')
        # create order to db
        print 'orderid=' + orderid

        reply_dict = dict()
        reply_dict['orderid'] = orderid
        body['sdk_param']['app_order'] = orderid
        reply_dict['sign'] = self._make_aichushop_sign(body['sdk_param'])
        return reply_dict

    def _handle_query_pay_ret(self, user_uid, body):
        reply_dict = dict()

        server_log.info('_handle_query_pay_ret by user_uid=' + user_uid)
        server_log.info('user_bills_going=' + str(self.application.user_bills_going))
        if user_uid in self.application.user_bills_going:
            bill_list = self.application.user_bills_going[user_uid]
            reply_dict['bills'] = deepcopy(bill_list)
            server_log.info('reply_dict=' + str(reply_dict))
            # syn to db
            self.application.db.bill.going.delete_one({'user_uid': user_uid})
            inc_fee = 0
            for v in bill_list:
                self.application.db.bill.completed.replace_one({'orderid': v['orderid']}, {
                    'user_uid': user_uid,
                    'orderid': v['orderid'],
                    'pay_code': v['pay_code'],
                    'fee': v['fee'],
                    'os': v['os'],
                    'service_id': v['service_id'],
                    'service_name': v['service_name'],
                    'userno': v['role_id'],
                    'complete_time': datetime.datetime.now()}, True)
                inc_fee += int(v['fee'])
            # 累积充值和充值记录
            if len(bill_list) > 0:
                self.application.db.bill.user.update_one(
                    {'user_uid': user_uid},
                    {
                        '$set': {
                            'userno': bill_list[0]['role_id']
                        },
                        '$push': {
                            'bills': {
                                '$each': bill_list
                            },
                        },
                        '$inc': {
                            'totalFee': inc_fee
                        }
                    },
                    True
                )

            del self.application.user_bills_going[user_uid]
        return reply_dict

    @staticmethod
    def _make_aichushop_sign(param_dict):
        union_str = ''
        server_log.info('make_aichushop by param_dict=' + str(param_dict))
        sorted_list = sorted(param_dict.iteritems(), key=lambda d: d[0], reverse=False)
        for v in sorted_list:
            # print v.encode('utf8')
            # if type(v) == int:
            #     print 'int v=' + str(v)
            #     union_str += str(v)
            # elif type(v) == str:
            #     print 'str v=' + v.encode('utf8')
            #     union_str += v.encode('utf8')

            print 'type=' + str(type(v[1]))
            # if type(v[1]) == dict:
            #     union_str += json.JSONEncoder().encode(v[1])
            # else:
            #     union_str += v[1].encode('utf8')

            union_str += v[1].encode('utf8')

        union_str += _APP_KEY
        server_log.info('make_aichushop by str=' + union_str)
        m = hashlib.md5()
        m.update(union_str)
        return m.hexdigest()


class AcspPayCbHandler(tornado.web.RequestHandler):
    def get(self):
        self.send_error()

    def post(self, *args, **kwargs):
        body = self.request.body
        server_log.info('AcspPayCb body=' + body)

        body_dict = urlparse.parse_qs(body)
        orderid = body_dict['appOrder'][0]
        otherinfo = json.JSONDecoder().decode(body_dict['otherInfo'][0])

        os = otherinfo['os']
        paycode = otherinfo['pay_code']
        service_id = otherinfo['service_id']
        service_name = otherinfo['service_name']
        userno = otherinfo['role_id']

        server_log.info('AcspPayCbHandler, format_user_uid: opencode=' + body_dict['openCode'][0] + ', os=' + str(os))
        user_uid = cfg.format_user_uid(body_dict['openCode'][0], str(os))

        if user_uid not in self.application.user_bills_going:
            user_bill = list()
            self.application.user_bills_going[user_uid] = user_bill
        else:
            user_bill = self.application.user_bills_going[user_uid]

        if orderid and paycode and os and service_id and service_name:
            bill_dict = {
                'orderid': orderid,
                'pay_code': paycode,
                'fee': body_dict['totalFee'][0],
                'os': os,
                'service_id': service_id,
                'service_name': service_name,
                'role_id': userno
            }
            user_bill.append(bill_dict)
            self.application.db.bill.going.update_one(
                {'user_uid': user_uid},
                {'$push': {
                    'bills': {
                        '$each': [bill_dict]
                    }
                }},
                True
            )
            server_log.info('AcspPayCbHandler paySuccess, orderid=' + orderid)

        self.write('Success')

if __name__ == "__main__":
    tornado.options.parse_command_line()
    cfg.setup_srvcfg(options.rt)
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(cfg.srvcfg['port_center'])
    tornado.ioloop.IOLoop.instance().start()


    # find_one 10000 times in 5w with index uses 2522ms
    # insert_one 10000 times in 5w(to 6w) with index uses 2662ms

    # test this !!!
    # http://127.0.0.1:12304/writeRecord?user_id=userid_ooxxooxx&user_key=key0123&record={}&callback=jQuery17204590415961574763_1441798647346&_=1441798742602


