# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import fields, api
from openerp.exceptions import ValidationError
import logging
import urllib2
import json
import requests

from urls import urls

_logger = logging.getLogger(__name__)


class WechatOfficeAccount(osv.Model):
    """
     微信公共账号
        access_token是公众号的全局唯一接口调用凭据，公众号调用各接口时都需使用access_token。开发者需要进行妥善保存。
    access_token的存储至少要保留512个字符空间。access_token的有效期目前为2个小时，需定时刷新，
    重复获取将导致上次获取的access_token失效.
    """
    _name = 'wechat.official.account'
    _description = 'wechat official account'

    name = fields.Char('name', help=u'微信公众账号名称')
    # token=JFXwtrG7wKf1T_PbdSO2HR21KOyBK7kHf7MotZgyg8Xh61ee0fv-H3r8_XMyoC8Z4FxgcEoqBZEbFUppxEYU5hyDFQ3pvILMsgcGdZyWMdg
    token = fields.Char('token',
                        default='JFXwtrG7wKf1T_PbdSO2HR21KOyBK7kHf7MotZgyg8Xh61ee0fv-H3r8_XMyoC8Z4FxgcEoqBZEbFUppxEYU5hyDFQ3pvILMsgcGdZyWMdg',
                        help=u'Token可由开发者可以任意填写，用作生成签名（该Token会和接口URL中包含的Token进行比对，从而验证安全性')
    encoding_aes_Key = fields.Char('EncodingAESKey', help=u'EncodingAESKey由开发者手动填写或随机生成，将用作消息体加解密密钥')
    app_id = fields.Char('app_id', default='wx2fade30990fa8ba8', help='', required=True)
    app_secret = fields.Char('app_secret', default='6e0344e8854f8d586983726a6924fd48',
                             help='', required=True)

    access_token = fields.Text('access_token', help=u'access token')
    expires_in = fields.Integer('expires_in', help=u'过期时间')
    developer_username = fields.Char('Developer UserName', help=u'开发者微信号', required=True)

    def get_access_token(self):
        """
        获取access_token:{"access_token":"ACCESS_TOKEN","expires_in":7200}
        @return:
        """
        url = urls['access_token_request_url']
        app_id = self.app_id
        app_secret = self.app_secret
        grant_type = 'client_credential'
        request_url = url + '?grant_type=%s&appid=%s&secret=%s' % (grant_type, app_id, app_secret)

        try:
            request = urllib2.urlopen(request_url)
            response = request.read()
            result = json.loads(response)
            if result.get('access_token', False):
                return {'success': True, 'result': result}
            else:
                return {'success': False, 'msg': str(result)}
        except Exception as e:
            _logger.error(e.message)
            return {'success': False, 'msg': e.message}

    @api.multi
    def update_access_token(self):
        """
        刷新access_token
        @return:
        """
        result = self.get_access_token()
        if result['success']:
            access_token = result['result']['access_token']
            expires_in = result['result']['expires_in']
            return self.write({'access_token': access_token, 'expires_in': expires_in})
        return False
