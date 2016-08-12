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


class WechatUserGroup(osv.Model):
    _name = 'wechat.user.group'
    _description = 'wechat user group'

    name = fields.Char('name')
    official_account_id = fields.Many2one('wechat.official.account', u'office account', required=True, help=u'公众账号')


class WechatUser(osv.Model):
    _name = 'wechat.user'
    _description = 'wechat user'

    name = fields.Char('name')
    official_account_id = fields.Many2one('wechat.official.account', u'office account', required=True, help=u'公众账号')
