# -*- coding: utf-8 -*-
"""
回复用户消息:
    当用户发送消息给公众号时（或某些特定的用户操作引发的事件推送时），
会产生一个POST请求，开发者可以在响应包（Get）中返回特定XML结构，来对
该消息进行响应（现支持回复文本、图片、图文、语音、视频、音乐）。严格来
说，发送被动响应消息其实并不是一种接口，而是对微信服务器发过来消息的一
次回复。微信服务器在五秒内收不到响应会断掉连接，并且重新发起请求，总共
重试三次.
    如果开发者希望增强安全性，可以在开发者中心处开启消息加密，这样，用
户发给公众号的消息以及公众号被动回复用户消息都会继续加密.
    假如服务器无法保证在五秒内处理并回复，必须做出下述回复，这样微信服
务器才不会对此作任何处理，并且不会发起重试（这种情况下，可以使用客服消息
接口进行异步回复），否则，将出现严重的错误提示。详见下面说明：
    1、（推荐方式）直接回复success
    2、直接回复空串（指字节长度为0的空字符串，而不是XML结构体中content字段的内容为空）
    一旦遇到以下情况，微信都会在公众号会话中，向用户下发系统提示“该公众号暂时无法提供服务，请稍后再试”：
    1、开发者在5秒内未回复任何内容
    2、开发者回复了异常数据，比如JSON数据等
"""
from openerp.osv import osv
from openerp import fields, api
from openerp.exceptions import ValidationError
import logging
import urllib2
import json
import requests
from urls import urls
import time

_logger = logging.getLogger(__name__)


class WechatReply(osv.Model):
    _name = 'wechat.reply'
    _description = 'replay user message'

    name = fields.Char(u'name')
    official_account_id = fields.Many2one('wechat.official.account', u'Official Account')

    ToUserName = fields.Char(u'ToUserName', default='', help=u'接收方帐号（收到的OpenID')
    FromUserName = fields.Char(u'FromUserName', default='', help=u'开发者微信号')
    CreateTime = fields.Integer(u'CreateTime', default=time.time(), help=u'消息创建时间(整型)')
    MsgType = fields.Selection(
        [('text', 'text'), ('image', 'image'), ('voice', 'voice'), ('video', 'video'), ('music', 'music'),
         ('news', 'news')], default='text', help=u'')

    Content = fields.Char(u'Content', default='', help=u'回复的消息内容（换行：在content中能够换行，微信客户端就支持换行显示')
    MediaId = fields.Char(u'MediaId', default='', help=u'通过素材管理接口上传多媒体文件，得到的id。')
    Title = fields.Char(u'Title', default='', help=u'视频消息的标题,非必填')
    Description = fields.Text(u'Description', default='', help=u'视频消息的描述,非必填')
    MusicUrl = fields.Char(u'MusicUrl', default='', help=u'音乐链接,非必填')
    HQMusicUrl = fields.Char(u'HQMusicUrl', default='', help=u'高质量音乐链接，WIFI环境优先使用该链接播放音乐,非必填')
    ThumbMediaId = fields.Char(u'ThumbMediaId', default='', help=u'缩略图的媒体id，通过素材管理接口上传多媒体文件，得到的id,非必填')
    ArticleCount = fields.Integer(u'ArticleCount', default=0, compute='compute_article_count', store=True,
                                  help=u'图文消息个数，限制为10条以内')
    item_ids = fields.One2many('wechat.reply.text.image.item', 'reply_id', string=u'text image items',
                               help=u'图文消息items')
    # 文本消息
    text_template = u'''
    <xml>
    <ToUserName><![CDATA[{toUser}]]></ToUserName>
    <FromUserName><![CDATA[{fromUser}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[{content}]]></Content>
    </xml>
    '''
    # 回复图片消息
    image_template = u'''
    <xml>
    <ToUserName><![CDATA[{toUser}]]></ToUserName>
    <FromUserName><![CDATA[{fromUser}]]></FromUserName>
    <CreateTime>{create_time}</CreateTime>
    <MsgType><![CDATA[image]]></MsgType>
    <Image>
    <MediaId><![CDATA[{media_id}]]></MediaId>
    </Image>
    </xml>
    '''
    # 回复语音消息
    voice_template = u'''
    <xml>
    <ToUserName><![CDATA[{toUser}]]></ToUserName>
    <FromUserName><![CDATA[{fromUser}]]></FromUserName>
    <CreateTime>{create_time} </CreateTime>
    <MsgType><![CDATA[voice]]></MsgType>
    <Voice>
    <MediaId><![CDATA[{media_id}]]></MediaId>
    </Voice>
    </xml>
    '''
    # 回复视频消息
    video_template = u'''
    <xml>
    <ToUserName><![CDATA[{toUser}]]></ToUserName>
    <FromUserName><![CDATA[{fromUser}]]></FromUserName>
    <CreateTime> {create_time} </CreateTime>
    <MsgType><![CDATA[video]]></MsgType>
    <Video>
    <MediaId><![CDATA[{media_id}]]></MediaId>
    <Title><![CDATA[{title}]]></Title>
    <Description><![CDATA[{description}]]></Description>
    </Video>
    </xml>
    '''
    # 回复音乐消息
    music_template = u'''
    <xml>
    <ToUserName><![CDATA[{toUser}]]></ToUserName>
    <FromUserName><![CDATA[{fromUser}]]></FromUserName>
    <CreateTime> {create_time} </CreateTime>
    <MsgType><![CDATA[music]]></MsgType>
    <Music>
    <Title><![CDATA[{title}]]></Title>
    <Description><![CDATA[{description}]]></Description>
    <MusicUrl><![CDATA[{music_url}]]></MusicUrl>
    <HQMusicUrl><![CDATA[{hq_music_url}]]></HQMusicUrl>
    <ThumbMediaId><![CDATA[{media_id}]]></ThumbMediaId>
    </Music>
    </xml>
    '''
    # 回复图文消息
    image_text_template = u'''
    <xml>
    <ToUserName><![CDATA[{toUser}]]></ToUserName>
    <FromUserName><![CDATA[{fromUser}]]></FromUserName>
    <CreateTime> {create_time} </CreateTime>
    <MsgType><![CDATA[news]]></MsgType>
    <ArticleCount>{article_account}</ArticleCount>
    <Articles>
    {item}
    </Articles>
    </xml>
    '''

    @api.one
    def compute_text_content(self):
        return self.text_template.format(toUser=self.ToUserName, fromUser=self.FromUserName,
                                         create_time=self.CreateTime, content=self.Content)

    @api.one
    def compute_image_content(self):
        return self.image_template.format(toUser=self.ToUserName, fromUser=self.FromUserName,
                                          create_time=self.CreateTime, media_id=self.MediaId)

    @api.one
    def compute_voice_content(self):
        return self.voice_template.format(toUser=self.ToUserName, fromUser=self.FromUserName,
                                          create_time=self.CreateTime, media_id=self.MediaId)

    @api.one
    def compute_video_content(self):
        return self.video_template.format(toUser=self.ToUserName, fromUser=self.FromUserName,
                                          create_time=self.CreateTime, media_id=self.MediaId,
                                          title=self.Title, description=self.Description)

    @api.one
    def compute_music_count(self):
        return self.music_template.format(toUser=self.ToUserName, fromUser=self.FromUserName,
                                          create_time=self.CreateTime, media_id=self.MediaId,
                                          title=self.Title, description=self.Description,
                                          music_url=self.MusicUrl, hq_music_url=self.HQMusicUrl)

    @api.depends('item_ids')
    @api.one
    def compute_article_count(self):
        self.ArticleCount = len(self.item_ids)

    @api.one
    def compute_article_content(self):
        items = ''
        for item in self.item_ids:
            items += item.item
        return self.image_text_template.format(toUser=self.ToUserName, fromUser=self.FromUserName,
                                               create_time=self.CreateTime,
                                               article_account=self.ArticleCount, item=items)

        # ArticleCount 是 图文消息个数，限制为10条以内
        # Articles 是  多条图文消息信息，默认第一个item为大图, 注意，如果图文数超过10，则将会无响应
        # Title  否  图文消息标题
        # Description 否 图文消息描述
        # PicUrl 否 图片链接，支持JPG、PNG格式，较好的效果为大图360 * 200，小图200 * 200
        # Url 否 点击图文消息跳转链接


class WechatReplyTextImageItem(osv.Model):
    _name = 'wechat.reply.text.image.item'
    _description = 'reply text_image_item'

    image_text_item_template = u'''
    <item>
    <Title><![CDATA[{title}]]></Title>
    <Description><![CDATA[{description}]]></Description>
    <PicUrl><![CDATA[{picurl}]]></PicUrl>
    <Url><![CDATA[{url}]]></Url>
    </item>
    '''

    Title = fields.Char(u'Title', default='', help=u'图文消息标题,非必填')
    Description = fields.Text(u'Description', default='', help=u'图文消息描述,非必填')
    PicUrl = fields.Char(u'PicUrl', default='', help=u'图片链接，支持JPG、PNG格式，较好的效果为大图360 * 200，小图200 * 200,非必填')
    Url = fields.Char(u'Url', default='', help=u'点击图文消息跳转链接,非必填')

    reply_id = fields.Many2one('wechat.reply', string=u'Reply Id', help=u'关联的回复id')
    item = fields.Text('item', compute='compute_item_content', store=True)

    @api.depends('Title', 'Description', 'PicUrl', 'Url')
    @api.one
    def compute_item_content(self):
        self.item = self.image_text_item_template.format(title=self.Title, description=self.Description,
                                                         picurl=self.PicUrl, url=self.Url)
