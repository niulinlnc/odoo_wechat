# -*- coding: utf-8 -*-
import functools
import logging
import urllib2
import random
import urlparse
import simplejson
import urlparse
import time
import hashlib
import os
import werkzeug.utils
from openerp import http
from openerp.http import request
from openerp.modules.registry import RegistryManager
from jinja2 import Environment, FileSystemLoader
# jinja2 env
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
templateLoader = FileSystemLoader(searchpath=BASE_DIR + "/templates")
htmlrender = Environment(loader=templateLoader)
# template = htmlrender.get_template("treeview.html")
# html = template.render({})
# return html

class Wechat(http.Controller):
    @http.route('/wechat/index/', auth='none', method='http')
    def wechat_index(self,**params):
        # https://open.weixin.qq.com/connect/oauth2/authorize?appid=APPID&redirect_uri=REDIRECT_URI&response_type=code&scope=SCOPE&state=STATE&connect_redirect=1#wechat_redirect
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        official_account=pool.get('wechat.official.account')
        default_account_id=official_account.search(cr,1,[])[0]
        default_account=official_account.browse(cr,1,default_account_id)
        access_token=default_account['access_token']
        app_id=default_account['app_id']
        app_secret=default_account['app_secret']
        token=default_account['token']
        return "access_token:%s<br/>app_id:%s<br>"%(access_token,app_id)


    @http.route('/wechat/getuser/',auth='none',methon='http',csrf=False)
    def wechat_get_user_info(self,**parmas):
        print parmas
