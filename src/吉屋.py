import os
import math

from config import config
from utils import common, gather, operation_file


class 吉屋:
    headers = config.universal_headers
    time_interval = 0

    citys_url = "http://www.jiwu.com/"
    plots_url = "{city_url}/loupan/esf/list-page{page}.html"

    citys_file_name = "./temp/吉屋_city.json"
    plots_file_name = "./data/吉屋/{city_name}.json"
    plots_dir_name = "./data/吉屋/"

    def __init__(self):
        pass

    def get_citys(self):
        '''获取城市列表
        访问城市列表 URL, 并将 HTML 转换为 etree 对象
        获取城市信息的 a 标签, 并从 a 标签中拿出城市名和城市 URL, 将这些数据保存到字典类型的变量中
        将数据保存到 JSON 文件中
        '''
        common.print_and_sleep('吉屋网：采集城市列表', time_interval=self.time_interval)
        etree = gather.get_html_to_etree(self.citys_url, headers=self.headers)
        citys_etree = etree.xpath('//div[@class="fivindexcont citymar"]//a')
        citys_dict = dict()
        for city_etree in citys_etree:
            city_name, city_url = city_etree.xpath('text()')[0], self.plots_url.format(city_url=city_etree.xpath('@href')[0], page="{page}")
            citys_dict[city_name] = {'city_name': city_name, 'city_url': city_url}
        operation_file.write_json_file(self.citys_file_name, citys_dict)

    def get_plots(self, city_name, city_url):
        '''采集当前城市小区基本数据
        访问当前城市的小区列表
        在第一页获取小区数量, 然后判断出最大页数
        循环页码, 组合小区列表页 url
        访问并将 html 转换为 etree 对象, 并获取小区相关数据标签 etree 对象
        采集小区列表中的 a 标签, 其中有小区名称和小区详情信息url
        循环结束, 当前城市小区基本数据采集结束, 保存至 JSON 文件中
        Args:
            city_name: 城市名
            city_url: 城市小区列表url
        '''
        page, max_page, plots_dict = 1, 1, dict()
        while page <= max_page:
            temp_url = city_url.format(page=page)
            common.print_and_sleep('吉屋网：采集{city_name}小区第{page}页: {url}'.format(city_name=city_name, page=page, url=temp_url), time_interval=self.time_interval)
            etree = gather.get_html_to_etree(temp_url, headers=self.headers)
            if page == 1:
                max_page = math.ceil(int(etree.xpath('//div[@class="txt"]/span/text()')[0]) / 20)
            for plot_etree in etree.xpath('//div[@class="tit"]/a'):
                plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                plots_dict[plot_name] = {'plot_name': plot_name, 'plot_url': plot_url}
            page += 1
        print('{city_name}小区采集完成，保存数据'.format(city_name=city_name))
        operation_file.write_json_file(self.plots_file_name.format(city_name=city_name), plots_dict)

    def get_plots_detail(self, file_path):
        '''获取当前城市的小区详细信息
        读取小区信息文件, 并循环每个小区信息
        判断此小区是否已采集过详细信息(这里按`地址`这个键来判断), 没有采集则采集详细信息
        每采集20个小区的详细信息则保存一次数据, 小区采集结束后也会保存一次数据
        Args:
            file_path: 单城市的小区信息文件
        '''
        plots_dict = operation_file.read_json_file(file_path)
        num = 1
        for key in plots_dict.keys():
            if plots_dict[key].get('地址') is None:
                plots_dict[key] = self._get_plot_detail(plots_dict[key])
                num += 1
            if num % config.save_file_number == 0:
                print('更新文件{file_path}'.format(file_path=file_path))
                operation_file.write_json_file(file_path, plots_dict)
        if num > 1:
            print('更新文件{file_path}'.format(file_path=file_path))
            operation_file.write_json_file(file_path, plots_dict)

    def _get_plot_detail(self, plot_dict):
        '''获取当前小区的详细信息
        访问小区的详情URL, 并获取 HTML 并转换为 etree 对象
        采集地址, 经纬度以及其他信息
        将采集的信息整合到旧字典中并返回
        Args:
            plot_dict: 小区的当前信息数据, 包含小区名和小区详情URL
        return:
            dict 小区的最新信息数据
        '''
        common.print_and_sleep('吉屋网: 采集{plot}详情: {url}'.format(plot=plot_dict['plot_name'], url=plot_dict['plot_url']), time_interval=self.time_interval)
        etree = gather.get_html_to_etree(plot_dict['plot_url'], headers=self.headers)
        try:  # 测试时, 一些小区回莫名其妙的报错, 并且在下次执行时又能正常执行, 所以报错时此小区跳过, 等下次执行时再次尝试
            plot_dict['经纬度'] = etree.xpath('//input[@id="lng"]/@value')[0] + ',' + etree.xpath('//input[@id="lat"]/@value')[0]
        except BaseException:
            return plot_dict
        plot_dict['地址'] = etree.xpath('//input[@id="address"]/@value')[0]
        plot_dict['城市'] = etree.xpath('//input[@id="cityName"]/@value')[0]
        plot_dict['区域'] = etree.xpath('//input[@id="areaName"]/@value')[0]
        other_details = etree.xpath('//div[@class="bottom xqxx"]/ul/li')
        for other_detail in other_details:
            try:  # 有值为空白的情况, 当为空白时, 获取的数据为 [], 会超出最大索引
                key, value = other_detail.xpath('span/text()')[0][:-1], other_detail.xpath('em/text()')[0]
                plot_dict[key] = value
            except BaseException:
                pass
        return plot_dict

    def run(self):
        '''执行函数
        第一步: 获取城市列表
        第二步: 获取每个城市的小区基本信息
        第三步: 获取所有小区的详情信息
        '''
        if os.path.exists(self.citys_file_name) is False:
            self.get_citys()
        for key, value in operation_file.read_json_file(self.citys_file_name).items():
            if os.path.exists(self.plots_file_name.format(city_name=key)) is False:
                self.get_plots(value['city_name'], value['city_url'])
        for file_name in os.listdir(self.plots_dir_name):
            self.get_plots_detail(self.plots_dir_name + file_name)
