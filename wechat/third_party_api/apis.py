# -*- coding: utf-8 -*-
"""
第三方api接入
百度语音识别
七牛云存储
"""
import requests
import base64
import json


# Baidu 语音识别
# App ID: 4810653
# API Key: LjL2tSwrKmnDLLEMPazCkEce
# Secret Key: E4IPseqzFbD7NeyzvPneXeKEo2dORLeR
class BaiDuVoice(object):
    voice_url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=%s&client_id=%s&client_secret=%s'
    grant_type = 'client_credentials'
    client_id = 'LjL2tSwrKmnDLLEMPazCkEce'
    client_secret = 'E4IPseqzFbD7NeyzvPneXeKEo2dORLeR'

    def __init__(self):
        pass

    def get_access_token(self):
        """
        @return:
                {
                "access_token": "1.a6b7dbd428f731035f771b8d********.86400.1292922000-2346678-124328",
                "expires_in": 86400,
                "refresh_token": "2.385d55f8615fdfd9edb7c4b********.604800.1293440400-2346678-124328",
                "scope": "public",
                "session_key": "ANXxSNjwQDugf8615Onqeik********CdlLxn",
                "session_secret": "248APxvxjCZ0VEC********aK4oZExMB",
            }
        """
        url = self.voice_url % (self.grant_type, self.client_id, self.client_secret)
        res = requests.request('get', url)
        return res.json()

    def analysis_voice(self, params={}):
        """
        format	sting	必填	语音压缩的格式，请填写上述格式之一，不区分大小写
        rate	int	必填	采样率，支持 8000 或者 16000
        channel	int	必填	声道数，仅支持单声道，请填写 1
        cuid	string	必填	用户唯一标识，用来区分用户，填写机器 MAC 地址或 IMEI 码，长度为60以内
        token	string	必填	开放平台获取到的开发者 access_token
        ptc	int	选填	协议号，下行识别结果选择，默认 nbest 结果
        lan	string	选填	语种选择，中文=zh、粤语=ct、英文=en，不区分大小写，默认中文
        url	string	选填	语音下载地址
        callback	string	选填	识别结果回调地址
        speech	string	选填	真实的语音数据 ，需要进行base64 编码
        len	int	选填	原始语音长度，单位字节
        其中，开发者可以把语音数据放在 JSON 序列的“speech”字段中，需要将语音先进行 base64编码，并标明语音数据的原始长度，
        填写“len”字段；也可以直接提供语音下载地址放在“url”字段中，并且提供识别结果的回调地址，放在“callback”参数中。
        因此“speech”和“len”参数绑定，“url”和“callback”参数绑定，这两组参数二选一填写，如果都填，默认处理第一种。

        这里选择base64编码
        @param voice:
        @return:
        """
        voice = params['voice']
        speech = base64.b64encode(voice)
        token = self.get_access_token()['access_token']

        data = dict()
        data['cuid'] = 'baidu_voice_analysis_voice'
        data['token'] = token
        data['format'] = params['format']
        data['channel'] = 1
        data['rate'] = 8000
        data['len'] = len(voice)
        data['speech'] = speech

        url = 'http://vop.baidu.com/server_api'
        res = requests.request('post', url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        return res


baidu = BaiDuVoice()


# 图灵机器人问答
class QARobot(object):
    """
    图灵机器人问答 ,回复用户发来的语音或文字

    Code	说明
    100000	文本类
    {
        "code":100000,
        "text":"你也好 嘻嘻"
    }
    200000	链接类
    {
        "code": 200000,
        "text": "亲，已帮你找到图片",
        "url": "http://m.image.so.com/i?q=%E5%B0%8F%E7%8B%97"
    }

    302000	新闻类
    {
        "code": 302000,
        "text": "亲，已帮您找到相关新闻",
        "list": [
            {
                "article": "工信部:今年将大幅提网速降手机流量费",
                "source": "网易新闻",
                "icon": "",
                "detailurl": "http://news.163.com/15/0416/03/AN9SORGH0001124J.html"
            },
            {
                "article": "北京最强沙尘暴午后袭沪 当地叫停广场舞",
                "source": "网易新闻",
                "icon": "",
                "detailurl": "http://news.163.com/15/0416/14/ANB2VKVC00011229.html"
            },
            {
                "article": "公安部:小客车驾照年内试点自学直考",
                "source": "网易新闻",
                "icon": "",
                "detailurl": "http://news.163.com/15/0416/01/AN9MM7CK00014AED.html"
            }
        ]
    }
    308000	菜谱类
    {
        "code": 308000,
        "text": "亲，已帮您找到菜谱信息",
        "list": [
            {
                "name": "鱼香肉丝",
                "icon": "http://i4.xiachufang.com/image/280/cb1cb7c49ee011e38844b8ca3aeed2d7.jpg",
                "info": "猪肉、鱼香肉丝调料 | 香菇、木耳、红萝卜、黄酒、玉米淀粉、盐",
                "detailurl": "http://m.xiachufang.com/recipe/264781/"
            }
        ]
    }
    313000（儿童版）	儿歌类
    314000（儿童版）	诗词类

    错误吗
    40001	参数key错误
    40002	请求内容info为空
    40004	当天请求次数已使用完
    40007	数据格式异常
    """

    @classmethod
    def get_reply(cls, info, userid):

        url = u"http://www.tuling123.com/openapi/api?key={key}&info={info}&userid={userid}"
        apikey = '1b674544c532430f9af0bfb80a6230c6'
        params = {
            "key": apikey,  # 您申请到的本接口专用的APPKEY
            "info": info,  # 要发送给机器人的内容，不要超过30个字符
            "userid": userid,  # 1~32位，此userid针对您自己的每一个用户，用于上下文的关联

        }
        res = requests.request('get', url.format(**params))
        try:
            data = res.json()
            if data['code'] == 100000:
                reply = data['text']
            elif data['code'] == 200000:
                reply = u"%s\n\n<a href='%s'>点击查看</a>\n" % (data['text'], data['url'])
            elif data['code'] == 302000:
                news = ''
                new_template = u"<a href='{url}'>{title}</a>\n\n"
                for new in data['list'][:5]:
                    news += new_template.format(url=new['detailurl'], title=new['article'])
                reply = u"%s\n\n%s\n" % (data['text'], news)
            elif data['code'] == 308000:
                menus = ''
                menu_template = u"<a href='{url}'>{title}</a>\n[{info}]\n\n"
                for menu in data['list'][:5]:
                    menus += menu_template.format(url=menu['detailurl'], title=menu['name'], info=menu['info'])
                reply = u"%s\n\n%s\n" % (data['text'], menus)
            else:
                reply = u'抱歉,我的主人出门了'
            return {'success': True, 'reply': reply}
        except Exception as e:
            return {'success': False, 'msg': e.message}
