# -*- coding: utf-8 -*-

from xml.etree import ElementTree

from utils import to_text


def parse_user_msg(params={}):
    """
    @param params: {
        xml str:微信传来的xml信息.
    }
    @return:
    """
    xml = params.get('xml', False)
    if not xml:
        return {}

    wechat_message = dict((child.tag, to_text(child.text))
                          for child in ElementTree.fromstring(xml))
    return wechat_message
    # wechat_message["raw"] = xml
    # wechat_message["type"] = wechat_message.pop("MsgType").lower()
    #
    # message_type = MESSAGE_TYPES.get(wechat_message["type"], UnknownMessage)
    # return message_type(wechat_message)
