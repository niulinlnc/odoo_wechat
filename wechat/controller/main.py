# -*- coding: utf-8 -*-
import functools
import logging
import base64
import urllib2
import random
import urlparse
import simplejson
import urlparse
import time
import hashlib
import werkzeug.utils
import openerp
from openerp import http, SUPERUSER_ID
from openerp.http import request
from werkzeug.wrappers import BaseResponse
from openerp.modules.registry import RegistryManager
from ..utils.parser import parse_user_msg
from ..utils.client import Client
from ..third_party_api.apis import baidu, QARobot

dict_openid = {}


class Wechat(http.Controller):
    # 介入微信第一步url,token,EncodingAESKey设置
    @http.route('/wechat/main/', type='http', auth='none', csrf=False)
    def wechat_main(self, **kwargs):
        """
        解析微信发来的消息,并保存到数据库中
        @param kwargs:
        @return:
        """
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        if len(kwargs) != 0:
            # 验证消息是否来自微信
            if self.check_signature(kwargs['signature'], kwargs['timestamp'], kwargs['nonce']):
                # 解析微信消息体
                message = parse_user_msg({'xml': request.httprequest.data})
                wechat_message = pool.get('wechat.message')
                new_message = wechat_message.browse(cr, openerp.SUPERUSER_ID,
                                                    wechat_message.create(cr, openerp.SUPERUSER_ID, message))

                # 如果没有消息体,说明是微信验证接口配置的token,直接返回echostr
                if not message:
                    return kwargs['echostr']
                else:
                    reply = self.get_reply(message=new_message)
                    if reply['success']:
                        return reply['reply']
                    else:
                        return ''
        else:
            return ''

    def check_signature(self, signature, timestamp, nonce):
        """
        验证消息真实性
        :param self:
        :param signature:
        :param timestamp:
        :param nonce:
        :return:
        """
        return True
        L = [timestamp, nonce, 'token']
        L.sort()
        s = L[0] + L[1] + L[2]
        return hashlib.sha1(s).hexdigest() == signature

    def get_reply(self, message):
        """
        根据消息获取回复
        @param message:
        @return:
        """
        msg_type = message['MsgType']
        if msg_type == 'voice':
            media = message.get_media_content()
            if media.get('success'):
                res = baidu.analysis_voice({'voice': media['media'], 'format': message['Format']})
                try:
                    info = res.json()['result'][0]
                except Exception as e:
                    logging.error(e.message)
                    return {'success': False, 'msg': e.message}
        elif msg_type == 'text':
            info = message['Content']
        else:
            return {'success': False, 'msg': ''}

        response = u'''<xml>
                        <ToUserName><![CDATA[{touser}]]></ToUserName>
                        <FromUserName><![CDATA[{fromuser}]]></FromUserName>
                        <CreateTime>12345678</CreateTime>
                        <MsgType><![CDATA[text]]></MsgType>
                        <Content><![CDATA[{content}]]></Content>
                        </xml>'''
        try:
            rebot_reply = QARobot.get_reply(info, message['FromUserName'])
            if rebot_reply['success']:
                content = rebot_reply['reply']
            else:
                logging.error(rebot_reply)
                content = u'抱歉!我不太明白!'
        except Exception as e:
            logging.error(e.message)
            content = u'抱歉!我不太明白!'
        reply = response.format(content=content, touser=message['FromUserName'],
                                fromuser=message['ToUserName'])
        return {'success': True, 'reply': reply}
