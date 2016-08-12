# -*- coding: utf-8 -*-
urls = {
    'access_token_request_url': 'https://api.weixin.qq.com/cgi-bin/token',  # 获取access_token的url
    'menu_request_url': 'https://api.weixin.qq.com/cgi-bin/menu/create',  # 微信菜单创建接口url
    'menu_get_url': 'https://api.weixin.qq.com/cgi-bin/menu/get',  # 查询微信中的菜单
    'menu_delete_all_url': 'https://api.weixin.qq.com/cgi-bin/menu/delete',  # 删除所有菜单包括个性化菜单
    'menu_conditional_url': 'https://api.weixin.qq.com/cgi-bin/menu/addconditional',  # 创建个性化菜单
    'menu_conditional_delete_url': 'https://api.weixin.qq.com/cgi-bin/menu/delconditional',  # 删除个性化菜单
    'download_media_url': 'http://file.api.weixin.qq.com/cgi-bin/media/get',  # 下载媒体文件
    'upload_news_url': 'https://api.weixin.qq.com/cgi-bin/material/add_news',  # 上传图文消息
    'upload_media_url': 'https://api.weixin.qq.com/cgi-bin/material/add_material',  # 删除永久媒体文件
    'upload_image_url': 'https://api.weixin.qq.com/cgi-bin/media/uploadimg',  # 删除永久媒体文件
    'delete_media_url': 'https://api.weixin.qq.com/cgi-bin/material/del_material',  # 删除永久媒体文件
}
