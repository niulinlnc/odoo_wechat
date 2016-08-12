# -*- coding: utf-8 -*-
"""
微信消息
当普通微信用户向公众账号发消息时，微信服务器将POST消息的XML数据包到开发者填写的URL上。
​在微信用户和公众号产生交互的过程中，用户的某些操作会使得微信服务器通过事件推送的形式通知
到开发者在开发者中心处设置的服务器地址，从而开发者可以获取到该信息。其中，某些事件推送在
发生后，是允许开发者回复用户的，某些则不允许，详细说明请见本页末尾的微信推送消息与事件说明。

"""
from openerp.osv import osv
from openerp import fields, api
from openerp.exceptions import ValidationError
import logging
import urllib2
import json
import requests
import base64
from urls import urls

_logger = logging.getLogger(__name__)


class WechatMessage(osv.Model):
    """
    微信发来的消息
    """
    _name = 'wechat.message'
    _description = 'wechat message'

    name = fields.Char('name')
    official_account_id = fields.Many2one('wechat.official.account', compute='compute_official_account', store=True,
                                          string=u'Official Account',
                                          help=u'公众账号')
    MsgType = fields.Selection([('text', u'文本'), ('image', u'图片'), ('voice', u'语音'), ('video', u'视屏'),
                                ('shortvideo', u'小视屏'), ('location', u'地理位置'), ('link', u'链接'),
                                ('event', u'事件')], u'MsgType', help=u'消息类型')
    ToUserName = fields.Char(u'ToUserName', help=u'开发者微信号')
    FromUserName = fields.Char(u'FromUserName', help=u'发送方帐号（一个OpenID')
    CreateTime = fields.Integer(u'CreateTime', help=u'消息创建时间 （整型）')
    MsgId = fields.Char(u'MsgId', help=u'消息id，64位整型')

    MediaId = fields.Char(u'MediaId', help=u'消息媒体id，可以调用多媒体文件下载接口拉取数据。')
    # MediaFile = fields.Many2one('ir.attachment', string=u'Media File', compute='get_media_file', store=True,
    #                             help=u'消息对应的媒体文件,通过接口从微信服务器下载')
    # 文本text
    Content = fields.Char(u'Content', help=u'文本内容')

    # 图片
    PicUrl = fields.Char(u'PicUrl', help=u'图片链接')
    PicMediaId = fields.Char(u'MediaId', related='MediaId', help=u'图片消息媒体id，可以调用多媒体文件下载接口拉取数据。')

    # 语音
    Format = fields.Char(u'Format', help=u'语音格式，如amr，speex等')
    Recognition = fields.Text(u'Recognition', help=u'开通语音识别后,Recognition为语音识别结果')
    VoiceMediaId = fields.Char(u'MediaId', related='MediaId', help=u'语音消息媒体id，可以调用多媒体文件下载接口拉取数据。')

    # 视屏
    ThumbMediaId = fields.Char(u'ThumbMediaId', help=u'视频消息缩略图的媒体id，可以调用多媒体文件下载接口拉取数据')
    VideoMediaId = fields.Char(u'MediaId', related='MediaId', help=u'视频消息媒体id，可以调用多媒体文件下载接口拉取数据。')

    # 小视屏
    ShortVideoThumbMediaId = fields.Char(u'ThumbMediaId', related='ThumbMediaId',
                                         help=u'视频消息缩略图的媒体id，可以调用多媒体文件下载接口拉取数据')
    ShortVideoMediaId = fields.Char(u'MediaId', related='MediaId', help=u'视频消息媒体id，可以调用多媒体文件下载接口拉取数据。')

    # 地理位置
    Location_X = fields.Char(u'Location_X', help=u'地理位置维度')
    Location_Y = fields.Char(u'Location_Y', help=u'地理位置经度')
    Scale = fields.Char(u'Scale', help=u'地图缩放大小')
    Label = fields.Char(u'Label', help=u'地理位置信息')

    # 链接
    Title = fields.Char(u'Title', help=u'消息标题')
    Description = fields.Text(u'Description', help=u'消息描述')
    Url = fields.Char(u'Url', help=u'消息链接')

    # 事件
    Event = fields.Selection(
        [('subscribe', 'subscribe'), ('unsubscribe', 'unsubscribe'), ('SCAN', 'SCAN'), ('LOCATION', 'LOCATION'),
         ('CLICK', 'CLICK'), ('VIEW', 'VIEW')], u'Event', help=u'事件类型')
    # 事件:扫码
    EventKey = fields.Char('EventKey',
                           help=u'''subscribe:事件KEY值，qrscene_为前缀，后面为二维码的参数值;
                                   SCAN:事件KEY值，是一个32位无符号整数，即创建二维码时的二维码scene_id;
                                   CLICK:事件KEY值，与自定义菜单接口中KEY值对应;
                                   VIEW:事件KEY值，设置的跳转URL''')
    Ticket = fields.Char('Ticket', help=u'二维码的ticket，可用来换取二维码图片')
    # 事件:位置
    Latitude = fields.Char(u'Latitude', help=u'地理位置纬度')
    Longitude = fields.Char(u'Longitude', help=u'地理位置经度')
    Precision = fields.Char(u'Latitude', help=u'地理位置精度')

    # 事件:点击菜单
    # EventKey = fields.Char('EventKey', help=u'CLICK:事件KEY值，与自定义菜单接口中KEY值对应,VIEW:事件KEY值，设置的跳转URL')

    @api.model
    def create(self, params={}):
        obj = super(WechatMessage, self).create(params)
        return obj

    @api.depends('ToUserName')
    @api.one
    def compute_official_account(self):
        official_account_id = self.env['wechat.official.account'].search(
            [('developer_username', '=', self.ToUserName)])
        if official_account_id:
            self.official_account_id = official_account_id[0]

    @api.model
    def get_media_content(self):
        # 下载媒体文件
        if self.MediaId:
            req_url = urls['download_media_url'] + '?access_token=%s&media_id=%s' % (
                self.official_account_id.access_token, self.MediaId)
            try:
                res = requests.request('get', req_url)
                try:
                    res.json()
                    logging.error(str(res.json()))
                except Exception as e:
                    media = res.content
                    return {'success': True, 'media': media}
            except Exception as e:
                logging.error(e.message)
                return {'success': False, 'msg': e.message}
        else:
            return {'success': False, 'msg': '非媒体消息'}

#
# class WechatMessageText(WechatMessageBase):
#     """
#     微信关注者发来的文本消息,MsgType=='text'
#     """
#     _name = 'wechat.message.text'
#     _inherit = 'wechat.message.base'
#     _description = 'Text Message'
#
#     # 文本text
#     Content = fields.Char(u'Content', help=u'文本内容')
#
#
# class WechatMessageImage(WechatMessageBase):
#     """
#     微信关注者发来的图片消息,MsgType=='image'
#     """
#     _name = 'wechat.message.image'
#     _inherit = 'wechat.message.base'
#     _description = 'Image Message'
#
#     PicUrl = fields.Char(u'PicUrl', help=u'图片链接')
#     MediaId = fields.Char(u'MediaId', help=u'图片消息媒体id，可以调用多媒体文件下载接口拉取数据。')
#
#
# class WechatMessageVoice(WechatMessageBase):
#     """
#     微信关注者发来的声音消息,MsgType=='voice'
#     """
#     _name = 'wechat.message.voice'
#     _inherit = 'wechat.message.base'
#     _description = 'Voice Message'
#
#     Format = fields.Char(u'Format', help=u'语音格式，如amr，speex等')
#     Recognition = fields.Char(u'Recognition', help=u'开通语音识别后,Recognition为语音识别结果')
#     MediaId = fields.Char(u'MediaId', help=u'语音消息媒体id，可以调用多媒体文件下载接口拉取数据。')
#
#
# class WechatMessageVideo(WechatMessageBase):
#     """
#     微信关注者发来的视屏消息,MsgType=='video'
#     """
#     _name = 'wechat.message.video'
#     _inherit = 'wechat.message.base'
#     _description = 'Video Message'
#
#     ThumbMediaId = fields.Char(u'ThumbMediaId', help=u'视频消息缩略图的媒体id，可以调用多媒体文件下载接口拉取数据')
#     MediaId = fields.Char(u'MediaId', help=u'视频消息媒体id，可以调用多媒体文件下载接口拉取数据。')
#
#
# class WechatMessageShortvideo(WechatMessageBase):
#     """
#     微信关注者发来的短视频消息,MsgType=='shortvideo'
#     """
#     _name = 'wechat.message.shortvideo'
#     _inherit = 'wechat.message.base'
#     _description = 'Short Video Message'
#
#     ThumbMediaId = fields.Char(u'ThumbMediaId', help=u'视频消息缩略图的媒体id，可以调用多媒体文件下载接口拉取数据')
#     MediaId = fields.Char(u'MediaId', help=u'视频消息媒体id，可以调用多媒体文件下载接口拉取数据。')
#
#
# class WechatMessageLocation(WechatMessageBase):
#     """
#     微信关注者发来的地理位置消息MsgType=='location'
#     """
#     _name = 'wechat.message.location'
#     _inherit = 'wechat.message.base'
#     _description = 'Location Message'
#
#     Location_X = fields.Char(u'Location_X', help=u'地理位置维度')
#     Location_Y = fields.Char(u'Location_Y', help=u'地理位置经度')
#     Scale = fields.Char(u'Scale', help=u'地图缩放大小')
#     Label = fields.Char(u'Label', help=u'地理位置信息')
#
#
# class WechatMessageLink(WechatMessageBase):
#     """
#     微信关注者发来的链接消息,MsgType=='link'
#     """
#     _name = 'wechat.message.link'
#     _inherit = 'wechat.message.base'
#     _description = 'Link Message'
#
#     Title = fields.Char(u'Title', help=u'消息标题')
#     Description = fields.Char(u'Description', help=u'消息描述')
#     Url = fields.Char(u'Url', help=u'消息链接')
#
#
# # 接收事件推送
#
# class WechatMessageEvent(WechatMessageBase):
#     """
#     接受微信事件推送,MsgType=='event'
#     """
#     _name = 'wechat.message.event'
#     _inherit = 'wechat.message.base'
#     _description = 'Event Message'
#
#     name = fields.Char('name')
#     official_account_id = fields.Many2one('wechat.official.account', u'office account', required=True, help=u'公众账号')
#     ToUserName = fields.Char(u'ToUserName', help=u'开发者微信号')
#     FromUserName = fields.Char(u'FromUserName', help=u'发送方帐号（一个OpenID')
#     CreateTime = fields.Integer(u'CreateTime', help=u'消息创建时间 （整型）')
#     MsgType = fields.Selection([('event', 'event')], 'MsgType', default='event')
#     Event = fields.Selection(
#         [('subscribe', 'subscribe'), ('unsubscribe', 'unsubscribe'), ('SCAN', 'SCAN'), ('LOCATION', 'LOCATION'),
#          ('CLICK', 'CLICK'), ('VIEW', 'VIEW')],
#         u'Event', help=u'时间类型')
#
#
# class WechatMessageEventSubscribe(WechatMessageEvent):
#     """
#         接受微信事件推送,用户subscribe(订阅),MsgType=='event',Event=='subscribe'
#         <xml>
#         <ToUserName><![CDATA[toUser]]></ToUserName>
#         <FromUserName><![CDATA[FromUser]]></FromUserName>
#         <CreateTime>123456789</CreateTime>
#         <MsgType><![CDATA[event]]></MsgType>
#         <Event><![CDATA[subscribe]]></Event>
#         </xml>
#     """
#     _name = 'wechat.message.event.subscribe'
#     _inherit = 'wechat.message.event'
#     _description = 'Event Message'
#
#     Event = fields.Selection([('subscribe', 'subscribe'), ('unsubscribe', 'unsubscribe')], u'Event',
#                              help=u'事件类型，subscribe(订阅)、unsubscribe(取消订阅)')
#
#
# class WechatMessageEventQr(WechatMessageEvent):
#     """
#         接受微信事件推送,扫码,用户未关注时，MsgType=='event',Event=='SCAN,subscribe'
#         <xml><ToUserName><![CDATA[toUser]]></ToUserName>
#         <FromUserName><![CDATA[FromUser]]></FromUserName>
#         <CreateTime>123456789</CreateTime>
#         <MsgType><![CDATA[event]]></MsgType>
#         <Event><![CDATA[subscribe]]></Event>
#         <EventKey><![CDATA[qrscene_123123]]></EventKey>
#         <Ticket><![CDATA[TICKET]]></Ticket>
#         </xml>
#     """
#     _name = 'wechat.message.event.qr'
#     _inherit = 'wechat.message.event'
#     _description = 'Event Message'
#
#     Event = fields.Selection([('subscribe', 'subscribe'), ('SCAN', 'SCAN')])
#     EventKey = fields.Char('EventKey',
#                            help=u'subscribe:事件KEY值，qrscene_为前缀，后面为二维码的参数值;'
#                                 u'SCAN:事件KEY值，是一个32位无符号整数，即创建二维码时的二维码scene_id')
#     Ticket = fields.Char('Ticket', help=u'二维码的ticket，可用来换取二维码图片')
#
#
# class WechatMessageEventLocation(WechatMessageEvent):
#     """
#         用户同意上报地理位置后，每次进入公众号会话时，都会在进入时上报地理位置，
#         或在进入会话后每5秒上报一次地理位置，公众号可以在公众平台网站中修改以上设置。
#         上报地理位置时，微信会将上报地理位置事件推送到开发者填写的URL。MsgType=='event',Event=='LOCATION'
#         <xml><ToUserName><![CDATA[toUser]]></ToUserName>
#         <FromUserName><![CDATA[FromUser]]></FromUserName>
#         <CreateTime>123456789</CreateTime>
#         <MsgType><![CDATA[event]]></MsgType>
#         <Event><![CDATA[subscribe]]></Event>
#         <EventKey><![CDATA[qrscene_123123]]></EventKey>
#         <Ticket><![CDATA[TICKET]]></Ticket>
#         </xml>
#     """
#     _name = 'wechat.message.event.location'
#     _inherit = 'wechat.message.event'
#     _description = 'Event Message'
#
#     Event = fields.Selection([('location', 'location')], default='location')
#     Latitude = fields.Char(u'Latitude', help=u'地理位置纬度')
#     Longitude = fields.Char(u'Longitude', help=u'地理位置经度')
#     Precision = fields.Char(u'Latitude', help=u'地理位置精度')
#
#
# class WechatMessageEventMenu(WechatMessageEvent):
#     """
#         用户点击自定义菜单后，微信会把点击事件推送给开发者，请注意，
#         点击菜单弹出子菜单，不会产生上报。，MsgType=='event',Event=='CLICK'
#         <xml>
#         <ToUserName><![CDATA[toUser]]></ToUserName>
#         <FromUserName><![CDATA[FromUser]]></FromUserName>
#         <CreateTime>123456789</CreateTime>
#         <MsgType><![CDATA[event]]></MsgType>
#         <Event><![CDATA[VIEW]]></Event>
#         <EventKey><![CDATA[www.qq.com]]></EventKey>
#         </xml>
#     """
#     _name = 'wechat.message.event.location'
#     _inherit = 'wechat.message.event'
#     _description = 'Event Message'
#
#     Event = fields.Selection([('CLICK', 'CLICK'), ('VIEW', 'VIEW')], default='CLICK')
#     EventKey = fields.Char('EventKey', help=u'CLICK:事件KEY值，与自定义菜单接口中KEY值对应,VIEW:事件KEY值，设置的跳转URL')
