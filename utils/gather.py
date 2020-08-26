import requests

from lxml import etree, html


def get_html(url, coding='UTF-8', **kwargv):
    res = requests.get(url, **kwargv)
    return res.content.decode(coding)


def get_html_to_etree(url, coding='UTF-8', **kwargv):
    '''访问网站获取 html，并将 html 转换为 etree 对象并返回
    Args:
        url: str 要访问的地址
        **kwargv: 访问时提交的参数， 如 headers、cookies 等
    return:
        etree 对象
    '''
    res = requests.get(url, **kwargv)
    html = res.content.decode(coding)
    return etree.HTML(html)


def etree2html(etree_obj, coding='UTF-8'):
    return html.tostring(etree_obj).decode(coding)
