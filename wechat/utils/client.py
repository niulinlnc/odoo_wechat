# -*- coding: utf-8 -*-

import time
import requests

from requests.compat import json as _json

# from werobot.utils import to_text
from openerp.osv import fields, osv, expression
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID

import logging
import time
from HTMLParser import HTMLParser

from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class ClientException(Exception):
    pass


to_text = {}

wx_errcode = {
    '-1': u'系统繁忙，此时请开发者稍候再试',
    '0': u'请求成功',
    '40001': u'获取access_token时AppSecret错误，或者access_token无效。请开发者认真比对AppSecret的正确性，或查看是否正在为恰当的公众号调用接口',
    '40002': u'不合法的凭证类型',
    '40003': u'不合法的OpenID，请开发者确认OpenID（该用户）是否已关注公众号，或是否是其他公众号的OpenID',
    '40004': u'不合法的媒体文件类型',
    '40005': u'不合法的文件类型',
    '40006': u'不合法的文件大小',
    '40007': u'不合法的媒体文件id',
    '40008': u'不合法的消息类型',
    '40009': u'不合法的图片文件大小',
    '40010': u'不合法的语音文件大小',
    '40011': u'不合法的视频文件大小',
    '40012': u'不合法的缩略图文件大小',
    '40013': u'不合法的AppID，请开发者检查AppID的正确性，避免异常字符，注意大小写',
    '40014': u'不合法的access_token，请开发者认真比对access_token的有效性（如是否过期），或查看是否正在为恰当的公众号调用接口',
    '40015': u'不合法的菜单类型',
    '40016': u'不合法的按钮个数',
    '40017': u'不合法的按钮个数',
    '40018': u'不合法的按钮名字长度',
    '40019': u'不合法的按钮KEY长度',
    '40020': u'不合法的按钮URL长度',
    '40021': u'不合法的菜单版本号',
    '40022': u'不合法的子菜单级数',
    '40023': u'不合法的子菜单按钮个数',
    '40024': u'不合法的子菜单按钮类型',
    '40025': u'不合法的子菜单按钮名字长度',
    '40026': u'不合法的子菜单按钮KEY长度',
    '40027': u'不合法的子菜单按钮URL长度',
    '40028': u'不合法的自定义菜单使用用户',
    '40029': u'不合法的oauth_code',
    '40030': u'不合法的refresh_token',
    '40031': u'不合法的openid列表',
    '40032': u'不合法的openid列表长度',
    '40033': u'不合法的请求字符，不能包含uxxxx格式的字',
    '40035': u'不合法的参数',
    '40038': u'不合法的请求格式',
    '40039': u'不合法的URL长度',
    '40050': u'不合法的分组id',
    '40051': u'分组名字不合法',
    '41001': u'缺少access_token参数',
    '41002': u'缺少appid参数',
    '41003': u'缺少refresh_token参数',
    '41004': u'缺少secret参数',
    '41005': u'缺少多媒体文件数据',
    '41006': u'缺少media_id参数',
    '41007': u'缺少子菜单数据',
    '41008': u'缺少oauth code',
    '41009': u'缺少openid',
    '42001': u'access_token超时，请检查access_token的有效期，请参考基础支持-获取access_token中，对access_token的详细机制说明',
    '42002': u'refresh_token超时',
    '42003': u'oauth_code超时',
    '43001': u'需要GET请求',
    '43002': u'需要POST请求',
    '43003': u'需要HTTPS请求',
    '43004': u'需要接收者关注',
    '43005': u'需要好友关系',
    '44001': u'多媒体文件为空',
    '44002': u'POST的数据包为空',
    '44003': u'图文消息内容为空',
    '44004': u'文本消息内容为空',
    '45001': u'多媒体文件大小超过限制',
    '45002': u'消息内容超过限制',
    '45003': u'标题字段超过限制',
    '45004': u'描述字段超过限制',
    '45005': u'链接字段超过限制',
    '45006': u'图片链接字段超过限制',
    '45007': u'语音播放时间超过限制',
    '45008': u'图文消息超过限制',
    '45009': u'接口调用超过限制',
    '45010': u'创建菜单个数超过限制',
    '45015': u'回复时间超过限制',
    '45016': u'系统分组，不允许修改',
    '45017': u'分组名字过长',
    '45018': u'分组数量超过上限',
    '46001': u'不存在媒体数据',
    '46002': u'不存在的菜单版本',
    '46003': u'不存在的菜单数据',
    '46004': u'不存在的用户',
    '47001': u'解析JSON/XML内容错误',
    '48001': u'api功能未授权，请确认公众号已获得该接口，可以在公众平台官网-开发者中心页中查看接口权限',
    '50001': u'用户未授权该api',
    '61451': u'参数错误(invalid parameter)',
    '61452': u'无效客服账号(invalid kf_account)',
    '61453': u'客服帐号已存在(kf_account exsited)',
    '61454': u'客服帐号名长度超过限制(仅允许10个英文字符，不包括@及@后的公众号的微信号)(invalid kf_acount length)',
    '61455': u'客服帐号名包含非法字符(仅允许英文+数字)(illegal character in kf_account)',
    '61456': u'客服帐号个数超过限制(10个客服账号)(kf_account count exceeded)',
    '61457': u'无效头像文件类型(invalid file type)',
    '61450': u'系统错误(system error)',
}


def check_error(json):
    """
    检测微信公众平台返回值中是否包含错误的返回码。
    如果返回码提示有错误，抛出一个 :class:`ClientException` 异常。否则返回 True 。
    """
    if "errcode" in json and json["errcode"] != 0:
        raise osv.except_osv(_(u'警告'), _("{}: {}".format(wx_errcode[str(json["errcode"])], json["errmsg"])))
    return json


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class Client(object):
    """
    微信 API 操作类
    通过这个类可以方便的通过微信 API 进行一系列操作，比如主动发送消息、创建自定义菜单等
    """

    def __init__(self, _self, cr, publi_account_id, appid, appsecret, token=None, token_expires_at=None):
        self.weixin = _self
        self.cr = cr
        self.publi_account_id = publi_account_id
        self.appid = appid
        self.appsecret = appsecret
        self._token = token
        self.token_expires_at = token_expires_at

    def request(self, method, url, **kwargs):
        print method, '-------------------'
        print url
        print kwargs
        if "params" not in kwargs:
            kwargs["params"] = {"access_token": self.token}
        if isinstance(kwargs.get("data", ""), dict):
            body = _json.dumps(kwargs["data"], ensure_ascii=False)
            body = body.encode('utf8')
            kwargs["data"] = body

        r = requests.request(
            method=method,
            url=url,
            **kwargs
        )
        r.raise_for_status()
        json = r.json()
        if check_error(json):
            return json

    def get(self, url, **kwargs):
        return self.request(
            method="get",
            url=url,
            **kwargs
        )

    def post(self, url, **kwargs):
        return self.request(
            method="post",
            url=url,
            **kwargs
        )

    def grant_token(self):
        """
        获取 Access Token 。
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=通用接口文档

        :return: 返回的 JSON 数据包
        """
        return self.get(
            url="https://api.weixin.qq.com/cgi-bin/token",
            params={
                "grant_type": "client_credential",
                "appid": self.appid,
                "secret": self.appsecret
            }
        )

    @property
    def token(self):

        if self.token_expires_at > 0:
            now = time.time()
            if self.token_expires_at - now > 60:
                return self._token

        obj = self.weixin.pool.get('cm.ex.weixin.appconnect')

        json = self.grant_token()
        self._token = json["access_token"]
        self.token_expires_at = int(time.time()) + json["expires_in"]

        parm = {
            'access_token': self._token,
            'token_expires_at': self.token_expires_at,
            'date_token': time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        }
        obj.write(self.cr, SUPERUSER_ID, self.publi_account_id, parm)

        return self._token

    def strip_tags(self, html):
        """
        清除html标签
        """

        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def create_menu(self, menu_data):
        """
        创建自定义菜单 ::

            client = Client("id", "secret")
            client.create_menu({
                "button":[
                    {
                        "type":"click",
                        "name":"今日歌曲",
                        "key":"V1001_TODAY_MUSIC"
                    },
                    {
                        "type":"click",
                        "name":"歌手简介",
                        "key":"V1001_TODAY_SINGER"
                    },
                    {
                        "name":"菜单",
                        "sub_button":[
                            {
                                "type":"view",
                                "name":"搜索",
                                "url":"http://www.soso.com/"
                            },
                            {
                                "type":"view",
                                "name":"视频",
                                "url":"http://v.qq.com/"
                            },
                            {
                                "type":"click",
                                "name":"赞一下我们",
                                "key":"V1001_GOOD"
                            }
                        ]
                    }
                ]})
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=自定义菜单创建接口

        :param menu_data: Python 字典

        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/menu/create",
            data=menu_data
        )

    def get_menu(self):
        """
        查询自定义菜单。
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=自定义菜单查询接口

        :return: 返回的 JSON 数据包
        """
        return self.get("https://api.weixin.qq.com/cgi-bin/menu/get")

    def delete_menu(self):
        """
        删除自定义菜单。
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=自定义菜单删除接口

        :return: 返回的 JSON 数据包
        """
        return self.get("https://api.weixin.qq.com/cgi-bin/menu/delete")

    def upload_media(self, media_type, media_file):
        """
        上传多媒体文件。
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=上传下载多媒体文件

        :param media_type: 媒体文件类型，分别有图片（image）、语音（voice）、视频（video）和缩略图（thumb）
        :param media_file:要上传的文件，一个 File-object

        :return: 返回的 JSON 数据包
        """

        return self.post(
            url="http://file.api.weixin.qq.com/cgi-bin/media/upload",
            params={
                "access_token": self.token,
                "type": media_type
            },
            files={
                "media": media_file
            }
        )

    def download_media(self, media_id):
        """
        下载多媒体文件。
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=上传下载多媒体文件

        :param media_id: 媒体文件 ID

        :return: requests 的 Response 实例
        """
        return requests.get(
            "http://file.api.weixin.qq.com/cgi-bin/media/get",
            params={
                "access_token": self.token,
                "media_id": media_id
            }
        )

    def create_group(self, name):
        """
        创建分组
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=分组管理接口

        :param name: 分组名字（30个字符以内）
        :return: 返回的 JSON 数据包

        """
        name = to_text(name)
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/groups/create",
            data={"group": {"name": name}}
        )

    def get_groups(self):
        """
        查询所有分组
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=分组管理接口

        :return: 返回的 JSON 数据包
        """
        return self.get("https://api.weixin.qq.com/cgi-bin/groups/get")

    def get_group_by_id(self, openid):
        """
        查询用户所在分组
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=分组管理接口

        :param openid: 用户的OpenID
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/groups/getid",
            data={"openid": openid}
        )

    def update_group(self, group_id, name):
        """
        修改分组名
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=分组管理接口

        :param group_id: 分组id，由微信分配
        :param name: 分组名字（30个字符以内）
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/groups/update",
            data={"group": {
                "id": int(group_id),
                "name": to_text(name)
            }}
        )

    # ok
    def move_user(self, user_id, group_id):
        """
        移动用户分组
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=分组管理接口

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param group_id: 分组 ID
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/groups/members/update",
            data={
                "openid": user_id,
                "to_groupid": group_id
            }
        )

    def get_user_info(self, user_id, lang="zh_CN"):
        """
        获取用户基本信息
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=获取用户基本信息

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param lang: 返回国家地区语言版本，zh_CN 简体，zh_TW 繁体，en 英语
        :return: 返回的 JSON 数据包
        """
        return self.get(
            url="https://api.weixin.qq.com/cgi-bin/user/info",
            params={
                "access_token": self.token,
                "openid": user_id,
                "lang": lang
            }
        )

    def get_followers(self, first_user_id=None):
        """
        获取关注者列表
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=获取关注者列表

        :param first_user_id: 可选。第一个拉取的OPENID，不填默认从头开始拉取
        :return: 返回的 JSON 数据包
        """
        params = {
            "access_token": self.token
        }
        if first_user_id:
            params["next_openid"] = first_user_id
        return self.get("https://api.weixin.qq.com/cgi-bin/user/get", params=params)

    def update_remark(self, openid, remark):
        """
        用户设置备注名
        详情请参考 https://api.weixin.qq.com/cgi-bin/user/info/updateremark?access_token=ACCESS_TOKEN

        :param openid: 用户id
        :param remark: 修改的名称
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/user/info/updateremark",
            data={
                "openid": openid,
                "remark": remark
            }
        )

    def send_text_message(self, user_id, content):
        """
        发送文本消息
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=发送客服消息

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param content: 消息正文
        :return: 返回的 JSON 数据包
        """

        content = self.strip_tags(content)
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            data={
                "touser": user_id,
                "msgtype": "text",
                "text": {"content": content}
            }
        )

    def send_image_message(self, user_id, media_id):
        """
        发送图片消息
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=发送客服消息

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param media_id: 图片的媒体ID。 可以通过 :func:`upload_media` 上传。
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            data={
                "touser": user_id,
                "msgtype": "image",
                "image": {
                    "media_id": media_id
                }
            }
        )

    def send_voice_message(self, user_id, media_id):
        """
        发送语音消息
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=发送客服消息

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param media_id: 发送的语音的媒体ID。 可以通过 :func:`upload_media` 上传。
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            data={
                "touser": user_id,
                "msgtype": "voice",
                "voice": {
                    "media_id": media_id
                }
            }
        )

    def send_video_message(self, user_id, media_id,
                           title=None, description=None):
        """
        发送视频消息
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=发送客服消息

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param media_id: 发送的视频的媒体ID。 可以通过 :func:`upload_media` 上传。
        :param title: 视频消息的标题
        :param description: 视频消息的描述
        :return: 返回的 JSON 数据包
        """
        video_data = {
            "media_id": media_id,
        }
        if title:
            video_data["title"] = title
        if description:
            video_data["description"] = description

        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            data={
                "touser": user_id,
                "msgtype": "video",
                "video": video_data
            }
        )

    def send_music_message(self, user_id, url, hq_url, thumb_media_id,
                           title=None, description=None):
        """
        发送音乐消息
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=发送客服消息

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param url: 音乐链接
        :param hq_url: 高品质音乐链接，wifi环境优先使用该链接播放音乐
        :param thumb_media_id: 缩略图的媒体ID。 可以通过 :func:`upload_media` 上传。
        :param title: 音乐标题
        :param description: 音乐描述
        :return: 返回的 JSON 数据包
        """
        music_data = {
            "musicurl": url,
            "hqmusicurl": hq_url,
            "thumb_media_id": thumb_media_id
        }
        if title:
            music_data["title"] = title
        if description:
            music_data["description"] = description

        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            data={
                "touser": user_id,
                "msgtype": "music",
                "music": music_data
            }
        )

    def send_article_message(self, user_id, articles):
        """
        发送图文消息
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=发送客服消息

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param articles: 一个包含至多10个 :class:`Article` 实例的数组
        :return: 返回的 JSON 数据包
        """
        articles_data = []
        for article in articles:
            articles_data.append({
                "title": article.title,
                "description": article.description,
                "url": article.url,
                "picurl": article.img
            })
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
            data={
                "touser": user_id,
                "msgtype": "news",
                "news": {
                    "articles": articles_data
                }
            }
        )

    def create_qrcode(self, **data):
        """
        创建二维码
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=生成带参数的二维码

        :param data: 你要发送的参数 dict
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/qrcode/create",
            data=data
        )

    def show_qrcode(self, ticket):
        """
        通过ticket换取二维码
        详情请参考 http://mp.weixin.qq.com/wiki/index.php?title=生成带参数的二维码

        :param ticket: 二维码 ticket 。可以通过 :func:`create_qrcode` 获取到
        :return: 返回的 Request 对象
        """
        return requests.get(
            url="https://mp.weixin.qq.com/cgi-bin/showqrcode",
            params={
                "ticket": ticket
            }
        )

    def send_preview(self, touser, msgtype, content):
        """
        预览接口

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param content: 消息正文
        :return: 返回的 JSON 数据包
        """

        # 文本
        if msgtype == 'text':
            return self.post(
                url="https://api.weixin.qq.com/cgi-bin/message/mass/preview",
                data={
                    "touser": touser,
                    "text": {
                        "content": content
                    },
                    "msgtype": msgtype
                }
            )
        # 图文消息
        if msgtype == 'mpnews':
            return self.post(
                url="https://api.weixin.qq.com/cgi-bin/message/mass/preview",
                data={
                    "touser": touser,
                    "mpnews": {
                        "media_id": content
                    },
                    "msgtype": msgtype
                }
            )
        # 语音
        if msgtype == 'voice':
            return self.post(
                url="https://api.weixin.qq.com/cgi-bin/message/mass/preview",
                data={
                    "touser": touser,
                    "voice": {
                        "media_id": content
                    },
                    "msgtype": "voice"
                }
            )

        # 图片
        if msgtype == 'image':
            return self.post(
                url="https://api.weixin.qq.com/cgi-bin/message/mass/preview",
                data={
                    "touser": touser,
                    "image": {
                        "media_id": content
                    },
                    "msgtype": msgtype
                }
            )
        # 视频
        if msgtype == 'video':
            return self.post(
                url="https://api.weixin.qq.com/cgi-bin/message/mass/preview",
                data={
                    "touser": touser,
                    "mpvideo": {
                        "media_id": content,
                    },
                    "msgtype": msgtype
                }
            )

    def send_preview_all(self, is_to_all, group_id, msgtype, content):
        """
        组群发

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param content: 消息正文
        :return: 返回的 JSON 数据包
        """
        url_https = "https://api.weixin.qq.com/cgi-bin/message/mass/sendall"

        # 文本
        if msgtype == 'text':
            return self.post(
                url=url_https,
                data={
                    "filter": {
                        "is_to_all": is_to_all,
                        "group_id": group_id
                    },
                    "text": {
                        "content": content
                    },
                    "msgtype": "text"
                }
            )
        # 图文消息
        if msgtype == 'mpnews':
            return self.post(
                url=url_https,
                data={
                    "filter": {
                        "is_to_all": is_to_all,
                        "group_id": group_id
                    },
                    "mpnews": {
                        "media_id": content
                    },
                    "msgtype": "mpnews"
                }
            )
        # 语音
        if msgtype == 'voice':
            return self.post(
                url=url_https,
                data={
                    "filter": {
                        "is_to_all": is_to_all,
                        "group_id": group_id
                    },
                    "voice": {
                        "media_id": content
                    },
                    "msgtype": "voice"
                }
            )

        # 图片
        if msgtype == 'image':
            return self.post(
                url=url_https,
                data={
                    "filter": {
                        "is_to_all": is_to_all,
                        "group_id": group_id
                    },
                    "image": {
                        "media_id": content
                    },
                    "msgtype": "image"
                }

            )
        # 视频
        if msgtype == 'video':
            return self.post(
                url=url_https,
                data={
                    "filter": {
                        "is_to_all": is_to_all,
                        "group_id": group_id
                    },
                    "mpvideo": {
                        "media_id": content,
                    },
                    "msgtype": "mpvideo"
                }

            )

    def send_preview_list(self, msgtype, touser, content):
        """
        列表群发

        :param user_id: 用户 ID 。 就是你收到的 `Message` 的 source
        :param content: 消息正文
        :return: 返回的 JSON 数据包
        """
        url_https = "https://api.weixin.qq.com/cgi-bin/message/mass/send"

        # 文本
        if msgtype == 'text':
            return self.post(
                url=url_https,
                data={
                    "touser": touser,
                    "msgtype": "text",
                    "text": {"content": content}
                }
            )
        # 图文消息
        if msgtype == 'mpnews':
            return self.post(
                url=url_https,
                data={
                    "touser": touser,
                    "mpnews": {
                        "media_id": content
                    },
                    "msgtype": "mpnews"
                }
            )
        # 语音：
        if msgtype == 'voice':
            return self.post(
                url=url_https,
                data={
                    "touser": touser,
                    "voice": {
                        "media_id": content
                    },
                    "msgtype": "voice"
                }

            )
        # 图片：
        if msgtype == 'image':
            return self.post(
                url=url_https,
                data={
                    "touser": touser,
                    "image": {
                        "media_id": content
                    },
                    "msgtype": "image"
                }

            )

        # 视频：
        if msgtype == 'video':
            return self.post(
                url=url_https,
                data={
                    "touser": touser,
                    "video": {
                        "media_id": content,
                        "title": "TITLE",
                        "description": "DESCRIPTION"
                    },
                    "msgtype": "video"
                }

            )

    def send_preview_del_msg_id(self, msg_id):
        """
        删除群发
        :param msg_id: 消息msg_id
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/mass/delete",
            data={
                "msg_id": msg_id
            }
        )

    def send_preview_mass_get(self, msg_id):
        """
        查询群发消息发送状态
        :param msg_id: 消息msg_id
        :return: 返回的 JSON 数据包
        """
        return self.post(
            url="https://api.weixin.qq.com/cgi-bin/message/mass/get",
            data={
                "msg_id": msg_id
            }
        )
