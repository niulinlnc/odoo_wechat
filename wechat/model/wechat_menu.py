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


class Menu(osv.Model):
    """
    自定义菜单管理
    """
    _name = 'wechat.custom.menu'
    _description = 'wechat custom-defined menu'

    name = fields.Char('name', help=u'菜单名称', required=True)
    menu_type = fields.Selection([('click', 'click'), ('view', 'view'), ('scancode_push', 'scancode_push'),
                                  ('scancode_waitmsg', 'scancode_waitmsg'), ('pic_sysphoto', 'pic_sysphoto'),
                                  ('pic_photo_or_album', 'pic_photo_or_album'), ('pic_weixin', 'pic_weixin'),
                                  ('location_select', 'location_select'), ('media_id', 'media_id'),
                                  ('view_limited', 'view_limited')], u'menu type', default='click', help=u'菜单类型')
    key = fields.Char('key', help=u'按钮为click类型时,需提供key')
    url = fields.Char('url', help=u'按钮类型为view时,需提供url')
    media_id = fields.Char('media id', help=u'按钮类型为["view_limited","media_id"]时,需提供media_id')
    official_account_id = fields.Many2one('wechat.official.account', u'office account', required=True, help=u'公众账号')
    parent_id = fields.Many2one('wechat.custom.menu', 'parent menu', help=u'上一级菜单')
    sub_button_ids = fields.One2many('wechat.custom.menu', 'parent_id', 'sub buttons', help=u'下一级菜单')

    is_root_menu = fields.Boolean(u'is root menu', default=False)

    @api.model
    def check_menu_number(self):
        """
        检查菜单数量是否合法,一级最多3个,二级最多5个
        @return:
        """
        official_account_id = self.official_account_id
        root_menus = self.search([('official_account_id', '=', official_account_id.id), ('is_root_menu', '=', True)])
        if len(root_menus) > 3:
            return {'success': False, 'msg': u'根菜单数量不能超过3个'}
        for root_menu in root_menus:
            if len(root_menu.sub_button_ids) > 5:
                return {'success': False, 'msg': u'二级菜单数量不能超过5个'}
        return {'success': True, 'msg': ''}

    @api.model
    def create(self, params):
        obj = super(Menu, self).create(params)
        check = obj.check_menu_number()
        if not check['success']:
            raise ValidationError(check['msg'])
        result = self.create_menu()
        if result['errcode'] != 0:
            raise ValidationError(result['errmsg'])
        return obj

    @api.multi
    def write(self, params):
        super(Menu, self).write(params)
        check = self.check_menu_number()
        if not check['success']:
            raise ValidationError(check['msg'])
        print self.parse_to_json_data()
        result = self.create_menu()
        if result['errcode'] != 0:
            raise ValidationError(result['errmsg'])
        return True

    @api.model
    def parse_to_json_data(self):
        """
            将公共账号下的菜单记录转成json格式
        @return:
        """
        official_account_id = self.official_account_id
        root_menus = self.search([('official_account_id', '=', official_account_id.id), ('is_root_menu', '=', True)])
        buttons = {'button': []}
        for root_menu in root_menus:
            button = {'name': root_menu.name}
            if root_menu.sub_button_ids:
                button['sub_button'] = []
                for sub_btn in root_menu.sub_button_ids:
                    sub_button = {'name': sub_btn.name, 'type': sub_btn.menu_type, "sub_button": []}
                    if sub_btn.menu_type == 'view':
                        sub_button['url'] = sub_btn.url
                    elif sub_btn.menu_type in ['media_id', 'view_limited']:
                        sub_button['media_id'] = sub_btn.media_id
                    else:
                        sub_button['key'] = sub_btn.key
                    button['sub_button'].append(sub_button)
            else:
                button['type'] = root_menu.menu_type
                if button['type'] == 'view':
                    button['url'] = root_menu.url
                elif button['type'] in ['media_id', 'view_limited']:
                    button['media_id'] = root_menu.media_id
                else:
                    button['key'] = root_menu.key
            buttons['button'].append(button)
        return json.dumps(buttons, ensure_ascii=False)

    @api.model
    def create_menu(self):
        """
        创建自定义菜单,使用post,每次更新菜单是必须带上全部菜单的json数据,否则会删除原有的菜单
        @return:
        """
        url = urls['menu_request_url']
        request_url = url + '?access_token=%s' % self.official_account_id.access_token
        post_data = self.parse_to_json_data()
        params = {'data': post_data.encode('utf-8')}
        res = requests.request('post', request_url, **params)
        return res.json()

    @api.model
    def search_menu(self):
        """
        查询微信中已有的菜单,结果中包含个性化菜单
        @return:
        """
        url = urls['menu_request_url']
        request_url = url + '?access_token=%s' % self.official_account_id.access_token
        res = requests.request('get', request_url)
        menus = res.json()
        print menus
        return menus

    @api.model
    def delete_menu(self):
        """
        删除微信中的菜单,包括个性化菜单
        @return:
        """
        url = urls['menu_delete_all_url']
        request_url = url + '?access_token=%s' % self.official_account_id.access_token
        res = requests.request('get', request_url)
        result = res.json()
        print result
        return result

    @api.model
    def create_conditional_menu(self):
        """
        添加个性化菜单
        @return:
        """
        pass

    @api.model
    def delete_conditional_menu(self):
        """
        删除个性化菜单
        @return:
        """
        url = urls['menu_conditional_delete_url']
        request_url = url + '?access_token=%s' % self.official_account_id.access_token
        res = requests.request('post', request_url)
        result = res.json()
        print result
        return result


class DIYMenu(osv.Model):
    """
    个性化菜单管理
    """
    _name = 'wechat.diy.menu'
    _description = 'wechat custom-defined menu'

    name = fields.Char('name', help=u'菜单名称', required=True)
    menu_type = fields.Selection([('click', 'click'), ('view', 'view'), ('scancode_push', 'scancode_push'),
                                  ('scancode_waitmsg', 'scancode_waitmsg'), ('pic_sysphoto', 'pic_sysphoto'),
                                  ('pic_photo_or_album', 'pic_photo_or_album'), ('pic_weixin', 'pic_weixin'),
                                  ('location_select', 'location_select'), ('media_id', 'media_id'),
                                  ('view_limited', 'view_limited')], u'menu type', default='click', help=u'菜单类型')
    key = fields.Char('key', help=u'按钮为click类型时,需提供key')
    url = fields.Char('url', help=u'按钮类型为view时,需提供url')
    media_id = fields.Char('media id', help=u'按钮类型为["view_limited","media_id"]时,需提供media_id')
    official_account_id = fields.Many2one('wechat.official.account', u'office account', required=True, help=u'公众账号')
    parent_id = fields.Many2one('wechat.custom.menu', 'parent menu', help=u'上一级菜单')
    sub_button_ids = fields.One2many('wechat.custom.menu', 'parent_id', 'sub buttons', help=u'下一级菜单')

    is_root_menu = fields.Boolean(u'is root menu', default=False)
