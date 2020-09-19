import os
import re

from utils import operation_file, common, gather
from config import config


class 搜楼啦:
    '''
    未解决问题:
        在腾讯云 centos 服务器上, 采集城市时会不定时报错, 在 windows 本地运行则无问题. 最开始怀疑是ip被禁, 但本地单线程无阻塞运行一个小时无封IP现象.
    目前此问题解决办法是, 这个不在 run.py 中执行, 而是手动在 test_run.py 中执行.
    '''
    headers = config.universal_headers

    citys_url = "http://www.souloula.com/"
    plots_url = "{city_domain}/xiaoqu/list_{page}.html"

    citys_file_name = "./temp/搜楼啦_city.json"
    plots_file_name = "./data/搜楼啦/{city_name}.json"
    plots_dir_name = "./data/搜楼啦/"

    citys_xpath = '//div[@class="ir"]/a'
    plots_xpath = '//div[@class="ni"]/a[1]'
    plots_error_xpath = '//div[@class="zhuan"]'
    详情_keys_xpath = '//div[@class="ri"]/b/text()'
    详情_values_xpath = '//div[@class="ri"]/text()'
    经纬度_re = "mp='(.*?)';"

    def __init__(self):
        pass

    def get_citys(self):
        '''获取城市列表
        访问城市列表 URL, 并将 HTML 转换为 etree 对象
        获取城市信息的 a 标签, 并从 a 标签中拿出城市名和城市 URL, 将这些数据保存到字典类型的变量中
        将数据保存到 JSON 文件中
        '''
        common.print_and_sleep('采集搜楼啦城市信息: {url}'.format(url=self.citys_url))
        citys_etree = gather.get_html_to_etree(self.citys_url, headers=self.headers)
        citys_dict = dict()
        for city_etree in citys_etree.xpath(self.citys_xpath):
            city_name, city_url = city_etree.xpath('text()')[0], city_etree.xpath('@href')[0]
            citys_dict[city_name] = {'city_name': city_name, 'city_url': city_url}
        operation_file.write_json_file(self.citys_file_name, citys_dict)

    def get_plots(self, city_name, city_url, plots_url):
        '''获取小区列表
        从第一页开始循环
        处理小区列表 URL(城市列表中的 URL 并非小区列表的 URL), 并访问, 然后将 HTML 转换为 etree 对象
        判断一个 class 为 zhuan 的 div 标签是否存在, 如果存在则说明此页没有数据, 也说明当前城市数据采集完毕, 终止循环
        获取小区列表中每个小区的名称及其 url, 并暂存到字典中, 在循环结束是保存到 JSON 文件中
        '''
        page, plots_dict = 1, dict()
        while True:
            temp_plots_url = plots_url.format(page=page)
            common.print_and_sleep('{city_name}城市小区采集第{page}页: {url}'.format(city_name=city_name, page=page, url=temp_plots_url))
            plots_etree = gather.get_html_to_etree(temp_plots_url, headers=self.headers)
            if len(plots_etree.xpath(self.plots_error_xpath)) >= 1:
                break
            for plot_etree in plots_etree.xpath(self.plots_xpath):
                plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                plots_dict[plot_name] = {'plot_name': plot_name, 'plot_url': city_url + plot_url}
            page += 1
        plots_file_name = self.plots_file_name.format(city_name=city_name)
        common.print_and_sleep('{city_name}城市小区采集结束,保存数据至{file_name}'.format(city_name=city_name, file_name=plots_file_name))
        operation_file.write_json_file(plots_file_name, plots_dict)

    def get_plots_detail(self, plots_file_name):
        '''获取文件中的小区详情数据
        读取小区数据文件中的数据, 遍历
        判断当前小区数据中是否存在`地址`数据, 如果存在则已经获取过详细数据了, 如果没有则获取
        没采集一定数量的小区详情数据, 就更新一次文件(防止因特殊情况中断采集, 导致采集的数据全部丢失)
        循环结束, 更新文件
        '''
        plots_dict = operation_file.read_json_file(plots_file_name)
        i = 1
        for plot_key in plots_dict.keys():
            if plots_dict[plot_key].get('经纬度') is None:
                common.print_and_sleep('采集{name}小区详情: {url}'.format(name=plots_dict[plot_key]['plot_name'], url=plots_dict[plot_key]['plot_url']))
                plots_dict[plot_key] = self._get_plot_detail(plots_dict[plot_key], plots_dict[plot_key]['plot_url'])
                i += 1
                if i % config.save_file_number == 0:
                    print('更新文件: {file_name}'.format(file_name=plots_file_name))
                    operation_file.write_json_file(plots_file_name, plots_dict)
        if i > 1:
            print('更新文件: {file_name}'.format(file_name=plots_file_name))
            operation_file.write_json_file(plots_file_name, plots_dict)

    def _get_plot_detail(self, plot_dict, url):
        '''获取某一小区的详细数据
        访问此小区详情URL, 获取 html 和 etree 对象
        获取小区详情信息, 此详情信息格式不规范, 需要逐个修正(xpath)
        获取小区经纬度(正则)
        将最新的数据返回
        '''
        html, etree = gather.get_html_and_etree(url, headers=self.headers)
        try:
            plot_dict.update(zip(etree.xpath(self.详情_keys_xpath), etree.xpath(self.详情_values_xpath)))
        except BaseException:
            plot_dict['地址'] = ''
            return plot_dict
        new_plot_dict = dict()
        for key in plot_dict.keys():
            if key == '小区地址：':
                new_plot_dict['地址'] = plot_dict[key]
                continue
            if key[-1:] == '：':
                new_plot_dict[key[:-1]] = plot_dict[key]
            else:
                new_plot_dict[key] = plot_dict[key]
        try:
            经纬度 = re.findall(self.经纬度_re, html)[0].split(',')
            经纬度.reverse()
            new_plot_dict['经纬度'] = ",".join(经纬度)
        except BaseException:
            new_plot_dict['经纬度'] = ''
        return new_plot_dict

    def run(self):
        '''执行函数
        第一步: 获取城市列表
        第二步: 获取每个城市的小区基本信息
        第三步: 获取所有小区的详情信息
        '''
        if os.path.exists(self.citys_file_name) is False:
            self.get_citys()
        for city_key, city_value in operation_file.read_json_file(self.citys_file_name).items():
            if os.path.exists(self.plots_file_name.format(city_name=city_value['city_name'])) is False:
                self.get_plots(city_value['city_name'], city_value['city_url'], self.plots_url.format(city_domain=city_value['city_url'], page="{page}"))
        for file_name in os.listdir(self.plots_dir_name):
            self.get_plots_detail(self.plots_dir_name + file_name)
