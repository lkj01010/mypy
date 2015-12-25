# -*- coding: UTF-8 -*-
import cfg
import tornado.httpclient
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import json
import pymongo
import time

from log import server_log

from tornado.options import define, options

define("rt", default='', help="reomote type", type=str)


class Application(tornado.web.Application):
    """this server directly save actions log of users to db"""

    def __init__(self):
        handlers = [
            (r"/writeStat", WriteStatToDBHandler),
            (r"/querySrvState", QuerySrvStateHandler),
            (r"/cmd", CommandHandler),
            (r"/rec", RecordSrvHandler),
        ]
        server_log.info('stat server start on port: ' + str(cfg.srvcfg['port_stat']) +
                        ' db[' + cfg.srvcfg['ip_mongodb'] + ':' + str(cfg.srvcfg['port_mongodb']) + ']')

        conn = pymongo.MongoClient(cfg.srvcfg['ip_mongodb'], cfg.srvcfg['port_mongodb'])
        self.db = conn[cfg.srvcfg['dbname_mongodb']]
        self.db.stat.create_index('user_uid')
        server_log.info('connect server OK')

        self.client = tornado.httpclient.AsyncHTTPClient()

        """server state"""
        self.server_running = True
        self.server_state_msg = ""

        """temp"""
        self.server_notice_msg = "【更新公告】<br/>《天天刀塔》等你来战！加入qq群专业客服为您解答各种疑惑！还可以同战友交流！<br/>更新内容：<br/>1.新增区服功能<br/>2.新增召唤师系统、装备系统、挂机功能<br/>3.新增竞技场商城及游戏内活动界面<br/>4.优化各关卡难度、玩法及各单位数值<br/>5.调整每日奖励内容、各礼包内容及价格<br/>qq群组：223105490	     客服QQ：800111767"
        # self.server_notice_msg = "【更新公告】<br/>《天天刀塔》等你来战！加入qq群专业客服为您解答各种疑惑！还可以同战友交流！<br/>更新内容：<br/>1.更新月卡及许愿池功能，详见游戏内“商城”及“许愿”界面<br/>2.新增“英雄礼包”，酒馆中新增“英雄征召”功能<br/>3.优化竞技场排名奖励、连胜荣誉奖励及购买次数<br/>4.调整首充礼包价格及内容，调整7日签到内容<br/>5.调整卡牌升级经验<br/>qq群组：223105490	     客服QQ：800111767"
        self.server_state_msg = self.server_notice_msg

        """last access"""
        self.db.lastaccess.create_index('user_uid')
        self.last_access_cache = dict()

        tornado.web.Application.__init__(self, handlers, debug=True)

    # def _set_state_msg(self):
        # msg_dict = dict()
        # msg_dict['gonggao'] = "亲爱的玩吧用户：<br/>    最好玩，最具有策略性的《天天刀塔》已经上线玩吧啦！马上邀请你的小伙伴一起战斗吧！<br/>游戏过程中不要忘记领取在线奖励和成就钻石哦！同时我们的全新的竞技场功能也将在近期开放！<br/>敬请期待吧！<br/><br/>QQ群组：223105490<br/>客服QQ：800111767"
           # "%e4%ba%b2%e7%88%b1%e7%9a%84%e7%8e%a9%e5%90%a7%e7%94%a8%e6%88%b7%ef%bc%9a%0d%0a++++%e6%9c%80%e5%a5%bd%e7%8e%a9%ef%bc%8c%e6%9c%80%e5%85%b7%e6%9c%89%e7%ad%96%e7%95%a5%e6%80%a7%e7%9a%84%e3%80%8a%e5%a4%a9%e5%a4%a9%e5%88%80%e5%a1%94%e3%80%8b%e5%b7%b2%e7%bb%8f%e4%b8%8a%e7%ba%bf%e7%8e%a9%e5%90%a7%e5%95%a6%ef%bc%81%e9%a9%ac%e4%b8%8a%e9%82%80%e8%af%b7%e4%bd%a0%e7%9a%84%e5%b0%8f%e4%bc%99%e4%bc%b4%e4%b8%80%e8%b5%b7%e6%88%98%e6%96%97%e5%90%a7%ef%bc%81%0d%0a%e6%b8%b8%e6%88%8f%e8%bf%87%e7%a8%8b%e4%b8%ad%e4%b8%8d%e8%a6%81%e5%bf%98%e8%ae%b0%e9%a2%86%e5%8f%96%e5%9c%a8%e7%ba%bf%e5%a5%96%e5%8a%b1%e5%92%8c%e6%88%90%e5%b0%b1%e9%92%bb%e7%9f%b3%e5%93%a6%ef%bc%81%e5%90%8c%e6%97%b6%e6%88%91%e4%bb%ac%e7%9a%84%e5%85%a8%e6%96%b0%e7%9a%84%e7%ab%9e%e6%8a%80%e5%9c%ba%e5%8a%9f%e8%83%bd%e4%b9%9f%e5%b0%86%e5%9c%a8%e8%bf%91%e6%9c%9f%e5%bc%80%e6%94%be%ef%bc%81%0d%0a%e6%95%ac%e8%af%b7%e6%9c%9f%e5%be%85%e5%90%a7%ef%bc%81%0d%0a%0d%0aQQ%e7%be%a4%e7%bb%84%ef%bc%9a223105490%0d%0a%e5%ae%a2%e6%9c%8dQQ%ef%bc%9a800111767"
#         msg_dict['gonggao'] = "亲爱的玩吧用户"
#         self.server_state_msg = str(msg_dict)


class WriteStatToDBHandler(tornado.web.RequestHandler):

    _MAX_ACTION_EACH_ID = 1000          # count of actions save to db each account

    def get(self):
        """as it is not a strictly important part, need not to check user certification"""
        user_uid = cfg.format_user_uid(self.get_argument('openid'), self.get_argument('user_pf'))
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        push_str = self.get_argument('stat')

        push_dict = json.JSONDecoder().decode(push_str)
        push_dict['modify_time'] = modify_time

        self.application.db.stat.update({'user_uid': user_uid},
                                        {
                                            '$push': {
                                                'actions': {
                                                    '$each': [push_dict],
                                                    '$slice': -WriteStatToDBHandler._MAX_ACTION_EACH_ID
                                                },
                                            },
                                            '$set': {
                                                'last_modify': modify_time
                                            }}, True, False)
        server_log.info(str(push_dict))
        self.write(str(self.get_argument('callback') + '(' + "{'ok': 1}" + ')'))

class QuerySrvStateHandler(tornado.web.RequestHandler):
    def get(self):
        callback = self.get_argument('callback')

        if self.application.server_running or self.get_argument('openid') in cfg.test_users:
            region_id = cfg.srvinfo['recommend']
            try:
                """get last access region info from cache or db, if has not, set recommend region"""
                user_uid = cfg.format_user_uid(self.get_argument('openid'), self.get_argument('user_pf'))
                if user_uid in self.application.last_access_cache:
                    region_id = self.application.last_access_cache[user_uid]
                else:
                    findret = self.application.db.lastaccess.find_one({'user_uid': user_uid})
                    if findret:
                        region_id = findret['region_id']
            except KeyError:
                pass

            reply_dict = dict()
            reply_dict['state'] = 1
            reply_dict['msg'] = self.application.server_state_msg
            reply_dict['srvinfo'] = cfg.srvinfo
            reply_dict['region_id'] = region_id
            reply = json.JSONEncoder().encode(reply_dict)
        else:
            reply = "{'state':0,'msg':'" + self.application.server_state_msg + "'}"
        reply = callback.encode('utf8') + '(' + reply + ')'
        server_log.info(reply)
        self.write(reply)

class CommandHandler(tornado.web.RequestHandler):

    def get(self):
        """
        type:0  停机维护
            msg：
        """
        print self.request.remote_ip
        if self.request.remote_ip == '127.0.0.1':
            command = self.get_argument('cmd')
            cmd_dict = json.JSONDecoder().decode(command)
            server_log.warn('cmd is: ' + str(cmd_dict))
            try:
                if cmd_dict["type"] == 0:
                    self.application.server_state_msg = cmd_dict["msg"]
                    self.application.server_running = False
                elif cmd_dict["type"] == 1:
                    self.application.server_state_msg = self.application.server_notice_msg
                    self.application.server_running = True

                srv_str = ""
                for v in cfg.srvcfg['srv_group']:
                    """存档服务器"""
                    addr_rec = cfg.addr_record(v)
                    request = tornado.httpclient.HTTPRequest(addr_rec + '/cmd', method='POST', body=command)
                    self.application.client.fetch(request, callback=CommandHandler.cmd_callback)

                    if cfg.srvcfg['channel'] == 1:
                        '''玩吧'''
                        """openapi服务器"""
                        request = tornado.httpclient.HTTPRequest(cfg.srvcfg['addr_tencent'] + '/cmd', method='POST',
                                                                 body=command)
                        self.application.client.fetch(request, callback=CommandHandler.cmd_callback)

                    srv_str += v + ' '
                self.write("send command to servers: " + v)
                # self.send_error()
            except KeyError:
                pass
        pass

    def post(self, *args, **kwargs):
        command_str = self.request.body
        command_dict = json.JSONDecoder().decode(command_str)
        server_log.warn('cmd is:\n ' + command_str)
        try:
            if command_dict["dest"] == 'record':
                for v in cfg.srvcfg['srv_group']:
                    """存档服务器"""
                    addr_rec = cfg.addr_record(v)
                    request = tornado.httpclient.HTTPRequest(addr_rec + '/cmd', method='POST',
                                                         body=command_dict['body'])
                    self.application.client.fetch(request, callback=CommandHandler.cmd_callback)

        except KeyError:
                self.write("{'ok': 0, 'msg': 'exception occur'}")

    @staticmethod
    def cmd_callback(response):
        print 'cmd callback msg: ', response.body

class RecordSrvHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        body = self.request.body
        bodydict = json.JSONDecoder().decode(body)
        try:
            if bodydict["type"] == 'last_access':
                user_uid = bodydict['body']['user_uid']
                region_id = bodydict['body']['region_id']
                if user_uid not in self.application.last_access_cache or \
                        region_id != self.application.last_access_cache[user_uid]:
                    self.application.last_access_cache[user_uid] = region_id
                    self.application.db.lastaccess.update({'user_uid': user_uid}, {'$set': {
                        'region_id': region_id
                    }}, True, False)

        except KeyError:
                self.write("{'ok': 0, 'msg': 'RecordSrvHandler exception occur'}")


if __name__ == "__main__":
    tornado.options.parse_command_line()
    cfg.setup_srvcfg(options.rt)
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(cfg.srvcfg['port_stat'])
    tornado.ioloop.IOLoop.instance().start()
