import requests

from lxml import etree


def get_html_to_etree(url, **kwargv):
    '''访问网站获取 html，并将 html 转换为 etree 对象并返回
    Args:
        url: str 要访问的地址
        **kwargv: 访问时提交的参数， 如 headers、cookies 等
    return:
        etree 对象
    '''
    city_res = requests.get(url, **kwargv)
    city_html = city_res.content.decode()
    return etree.HTML(city_html)
