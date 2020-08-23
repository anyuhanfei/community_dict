import os
import math
import time

from config import config
from utils import gather, json


class 链家:
    city_url = "https://www.lianjia.com/city/"

    def __init__(self):
        self.have_city_json = os.path.exists(config.链家_city_json_file_name)

    def get_citys(self):
        city_etree = gather.get_html_to_etree(self.city_url, headers=config.universal_headers)
        # 获取城市的 a 标签代码块
        city_etree = city_etree.xpath('//div[@class="city_province"]/ul/li/a')
        citys = dict()
        for i in range(0, len(city_etree)):
            citys[i] = {'city_name': city_etree[i].xpath('text()')[0], 'city_url': city_etree[i].xpath('@href')[0]}
        json.write_json_file(config.链家_city_json_file_name, citys)

    def get_plots(self):
        citys = json.read_json_file(config.链家_city_json_file_name)

        for i in range(0, len(citys)):
            city_name, city_url = citys[str(i)]['city_name'], config.链家_plot_list_url.format(city_url=citys[str(i)]['city_url'], page="{page}")
            if os.path.exists(config.链家_plot_json_file_name.format(file_name=city_name)) is True or city_url.find('fang') != -1:
                continue
            # 循环全部列表
            page_maximum, page, plot_dict = 1, 1, dict()
            while page <= page_maximum:
                plot_url = city_url.format(page=page)
                # 采集
                print('开始采集：{url}'.format(url=plot_url))
                plot_etree = gather.get_html_to_etree(plot_url, headers=config.universal_headers)
                # 获取最大页码
                if page_maximum == 1 and page == 1:
                    try:
                        page_maximum = math.ceil(int(plot_etree.xpath('//h2[@class="total fl"]/span/text()')[0]) / 30)
                    except BaseException:
                        print('跳过URL：{url}'.format(url=plot_url))
                # 获取小区名称及url
                plot_etree_list = plot_etree.xpath('//div[@class="info"]/div[@class="title"]/a')
                for plot_etree in plot_etree_list:
                    plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                    plot_dict[plot_name] = {'plot_name': plot_name, 'plot_url': plot_url}
                # 下次循环的准备
                page += 1
                time.sleep(config.time_interval)
            # 将数据保存至文件中
            json.write_json_file(config.链家_plot_json_file_name.format(file_name=city_name), plot_dict)

    def index(self):
        if self.have_city_json is False:
            self.get_citys()
        self.get_plots()
