import os
import math
import time

from config import config
from utils import gather, operation_file


class 链家:
    '''采集链家网的小区数据'''
    city_url = config.链家_city_list_url

    city_list_xpath = '//div[@class="city_province"]/ul/li/a'
    page_maximum_xpath = '//h2[@class="total fl"]/span/text()'
    plot_list_xpath = '//div[@class="info"]/div[@class="title"]/a'

    def __init__(self):
        self.have_city_json = os.path.exists(config.链家_city_json_file_name)

    def get_citys(self):
        '''获取城市列表
        访问城市列表 URL 并将得到的 HTML 转换为 etree 对象
        从 etree 对象中得到城市信息所在的 a 标签
        从 a 标签中取出城市名和城市对应的 URL, 保存至 JSON 文件中
        '''
        city_etree = gather.get_html_to_etree(self.city_url, headers=config.universal_headers)
        city_etree = city_etree.xpath(self.city_list_xpath)
        citys = dict()
        for i in range(0, len(city_etree)):
            citys[i] = {'city_name': city_etree[i].xpath('text()')[0], 'city_url': config.链家_plot_list_url.format(city_url=city_etree[i].xpath('@href')[0], page="{page}")}
        operation_file.write_json_file(config.链家_city_json_file_name, citys)

    def get_all_city_plots(self):
        '''获取所有城市的小区
        读取城市列表 JSON 文件, 获取全部城市列表(字典类型)
        循环城市列表, 获取城市名和对应的 URL, 当前获取的 URL 与展示小区列表的 URL 不同
        判断当前城市小区的 JSON 文件是否存在, 如果存在则说明此城市已完成采集, 跳过当前城市
        通过判断则采集当前城市小区数据
        '''
        citys = operation_file.read_json_file(config.链家_city_json_file_name)

        for i in range(0, len(citys)):
            city_name, city_url = citys[str(i)]['city_name'], citys[str(i)]['city_url']
            if os.path.exists(config.链家_plot_json_file_name.format(file_name=city_name)) is True:
                continue
            self._get_plots(city_name, city_url)

    def _get_plots(self, city_name, city_url):
        '''获取城市中的小区
        初始化当前页码, 最大页码使其能通过循环的判定
        将当前页码与 URL 组合, 访问此 URL 并将 HTMl 转换为 etree 对象
        第一次循环, 需要采集到最大页码 (此处如果报错, 说明当前城市无小区信息或者被服务端检测到并拦截了)
        从 etree 对象中得到小区信息所在的 a 标签
        从 a 标签中取出小区名和小区对应的详情信息 URL
        当前城市小区采集结束后, 保存数据至 JSON 文件
        Args:
            city_name: 城市名称
            city_url: 城市对应的首页地址(非城市的小区地址)
        return:
            none
        '''
        # 循环全部列表
        page_maximum, page, plot_dict = 1, 1, dict()
        while page <= page_maximum:
            plot_url = city_url.format(page=page)
            print('开始采集：{url}'.format(url=plot_url))
            plot_etree = gather.get_html_to_etree(plot_url, headers=config.universal_headers)
            # 获取最大页码
            if page_maximum == 1 and page == 1:
                try:
                    page_maximum = math.ceil(int(plot_etree.xpath(self.page_maximum_xpath)[0]) / 30)
                except BaseException:
                    print('获取最大页码异常, 跳过当前城市: {city_name}'.format(city_name=city_name))
                    return
            # 获取小区名称及url
            plot_etree_list = plot_etree.xpath(self.plot_list_xpath)
            for plot_etree in plot_etree_list:
                plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                plot_dict[plot_name] = {'plot_name': plot_name, 'plot_url': plot_url}
            # 下次循环的准备
            page += 1
            time.sleep(config.time_interval)
        # 将数据保存至文件中
        operation_file.write_json_file(config.链家_plot_json_file_name.format(file_name=city_name), plot_dict)

    def run(self):
        '''采集器运行
        第一步: 采集城市列表
        第二步: 采集城市小区的基本数据
        第三步: 采集小区的详细数据
        '''
        if self.have_city_json is False:
            self.get_citys()
        self.get_all_city_plots()
