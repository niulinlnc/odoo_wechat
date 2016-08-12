# -*- coding: utf-8 -*-
{
    'name': '微信接入',
    'summary': '',
    'version': '1.0',
    'category': 'application',
    'sequence': 0,
    'author': 'Merlin Gao',
    'website': 'http://www.odoo-modules.com',
    'depends': ['base'],
    'data': [
        'view/wechat_view.xml',
        'view/wechat_message_view.xml',
        'view/wechat_reply_view.xml',
        'view/wechat_media_view.xml',
        'view/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'description': """
    将微信接入到odoo中
""",
}
