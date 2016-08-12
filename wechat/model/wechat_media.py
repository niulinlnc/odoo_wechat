# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp import fields, api
from openerp.exceptions import ValidationError
import logging
import urllib2
import json
import base64
import requests
from urls import urls
import subprocess
import uuid
import tempfile

_logger = logging.getLogger(__name__)


class WechatMedia(osv.Model):
    _name = 'wechat.media'
    _description = 'wechat media'

    name = fields.Char('name')
    official_account_id = fields.Many2one('wechat.official.account', u'office account', required=True, help=u'公众账号')
    media_type = fields.Selection([('image', u'图片'), ('voice', u'语音'), ('video', u'视屏'), ('thumb', u'缩略图')],
                                  string=u'MediaType', help=u'媒体类型', required=True)
    video_title = fields.Char(u'VideoTitle', help=u'视频素材的标题')
    video_introduction = fields.Text(u'VideoIntroduction', help=u'视频素材的描述')
    media_file = fields.Binary('ir.attachment', help=u'媒体文件', required=True)
    media_id = fields.Char('MediaId')

    @api.model
    @api.multi
    def create_media(self):
        """
         上传到微信
        @return:
        """
        media_type = self.media_type
        data = dict()
        data['type'] = media_type
        data['media'] = self.media_file
        if media_type == 'image':
            url = urls['upload_image_url']
            data = {'media': self.media_file}
        elif media_type == 'video':
            data['title'] = self.video_title
            data['introduction'] = self.video_introduction
            url = urls['upload_media_url']
        else:
            url = urls['upload_media_url']
        url += '?access_token=%s' % self.official_account_id.access_token

        tmp_file = '/tmp/%s.png' % str(uuid.uuid1())
        tmp = open(tmp_file, 'wb')
        tmp.write(base64.b64decode(self.media_file))
        tmp.close()
        # media = tempfile.TemporaryFile()
        # media.write(base64.b64decode(self.media_file))
        up = subprocess.Popen(['curl', '-F', 'media=@%s' % tmp_file, url], stdout=subprocess.PIPE)
        res = up.stdout.read()
        result = json.loads(res)
        print result
        # res = requests.request('post', url, files={'media': base64.b64decode(self.media_file)})
        # result = res.json()

    @api.model
    @api.multi
    def delete_media(self):
        """
        删除图文消息
        @return:
        """
        url = urls['delete_media_url'] + '?access_token=%s' % self.official_account_id.access_token
        data = {'media_id': self.media_id}
        res = requests.request('post', url, data=json.dumps(data))
        data = res.json()
        print data

    @api.model
    def create(self, params={}):
        obj = super(WechatMedia, self).create(params)
        obj.create_media()
        return obj

    @api.model
    def unlink(self):
        self.delete_media()
        super(WechatMedia, self).unlink()

    @api.model
    @api.multi
    def write(self, params={}):
        """
        更新图文消息,先删除原有的消息,在上传新的
        @param params:
        @return:
        """
        self.delete_media()
        super(WechatMedia, self).write(params)
        self.create_media()


class WechatNews(osv.Model):
    """
    图文消息
    """
    _name = 'wechat.news'
    _description = 'wechat news'

    name = fields.Char(u'Name')
    official_account_id = fields.Many2one('wechat.official.account', string=u'OfficialAccount', required=True,
                                          help=u'公众号')
    title = fields.Char(u'Title', help=u'标题', required=True)
    thumb_media_id = fields.Char(u'ThumbMediaId', help=u'图文消息的封面图片素材id（必须是永久mediaID', required=True)
    author = fields.Char(u'Author', help=u'作者', required=True)
    digest = fields.Char(u'Digest', required=True, help=u'图文消息的摘要，仅有单图文消息才有摘要，多图文此处为空')
    show_cover_pic = fields.Selection([(0, u'否'), (1, u'是')], string=u'ShowCoverPic',
                                      help=u'是否显示封面，0为false，即不显示，1为true，即显示', required=True)
    content = fields.Html(u'Content', help=u'图文消息的具体内容，支持HTML标签，必须少于2万字符，小于1M，且此处会去除JS', required=True)
    content_source_url = fields.Char(u'ContentSourceUrl', help=u'图文消息的原文地址，即点击“阅读原文”后的URL', required=True)

    media_id = fields.Char(u'MediaId', help=u'上传成功后,微信返回的media_id', readonly=True)

    @api.model
    @api.multi
    def create_media(self):
        """
        上传图文消息文件到微信
        @return:
        """
        url = urls['upload_media_url'] + '?access_token=%s' % self.official_account_id.access_token
        data = dict()
        data['articles'] = []
        article = dict()
        article['title'] = self.title
        article['thumb_media_id'] = self.thumb_media_id
        article['author'] = self.author
        article['digest'] = self.digest
        article['show_cover_pic'] = self.show_cover_pic
        article['content'] = self.content
        article['content_source_url'] = self.content_source_url
        data['articles'].append(article)
        res = requests.request('post', url, data=json.dumps(data))
        result = res.json()
        self.media_id = result['media_id']

    @api.model
    def create_news_image(self):
        """
        将图文消息中的图片上传到微信
        @return:
        """
        pass

    @api.model
    @api.one
    def delete_media(self):
        """
        删除图文消息
        @return:
        """
        url = urls['delete_media_url'] + '?access_token=%s' % self.official_account_id.access_token
        data = {'media_id': self.media_id}
        res = requests.request('post', url, data=json.dumps(data))
        result = res.json()
        print result

    @api.model
    def create(self, params={}):
        """
        @param params:
        @return:
        """
        obj = super(WechatNews, self).create(params)
        return obj

    @api.model
    def unlink(self):
        self.delete_media()
        super(WechatNews, self).unlink()

    @api.model
    @api.multi
    def write(self, params={}):
        """
        更新图文消息,先删除原有的消息,在上传新的
        @param params:
        @return:
        """
        self.delete_media()
        super(WechatNews, self).write(params)
        self.create_media()
