import os
import re

from config import config
from utils import common, gather, operation_file


class 房产超市:
    citys_url = config.房产超市_citys_url
    plots_url = config.房产超市_plots_url

    headers = config.universal_headers

    coding = "GB18030"

    citys_xpath = '//ul[@class="citylist"]/li/a'
    plots_xpath = '//div[@class="list-wrap2"]/table/tr/td[1]/a'
    地址_xpath = '//div[@class="addr"]/text()'
    地址链_xpath = '//div[@class="curmbs"]/a/text()'
    详情_keys_xpath = '//div[@class="num xiaoqu_info"]/dl/dt/text()'
    详情_values_xpath = '//div[@class="num xiaoqu_info"]/dl/dd/text()'
    经度_re = 'bmapx=(.*?);'
    纬度_re = 'bmapy=(.*?);'

    citys_file_name = config.房产超市_citys_file_name
    plots_file_name = config.房产超市_plots_file_name
    plots_dir_name = config.房产超市_plots_dir_name

    def __init__(self):
        pass

    def get_citys(self):
        '''获取城市列表
        访问城市列表 URL, 并将 HTML 转换为 etree 对象
        获取城市信息的 a 标签, 并从 a 标签中拿出城市名和城市 URL, 将这些数据保存到字典类型的变量中
        将数据保存到 JSON 文件中
        '''
        city_list_etree = gather.get_html_to_etree(self.citys_url, coding=self.coding, headers=self.headers)
        city_dict = dict()
        for city_etree in city_list_etree.xpath(self.citys_xpath):
            city_name, city_url = city_etree.xpath('text()')[0], city_etree.xpath('@href')[0]
            city_dict[city_name] = {'city_name': city_name, 'city_url': city_url}
        operation_file.write_json_file(self.citys_file_name, city_dict)

    def get_plots(self, city_name, city_url):
        '''获取小区列表
        处理小区列表 URL(城市列表中的 URL 并非小区列表的 URL)
        每个城市的小区列表有两个变量, 一个是区域(包含城市自身和周边辖区, 从1开始按数字排序), 另一个是页码
        一层循环, 循环区域num, 当前区域的第一页小区列表在此获取, 可以判定当前区域num中是否有小区列表, 如果没有则说明是无效区域, 则当前城市小区采集结束
        二层循环, 循环页码, 从页码2开始采集(页码1已经采集过了), 同样根据是否有小区列表来判定此区域是否采集完成
        将数据保存到 JSON 文件中
        '''
        plots_url = self.plots_url.format(city_url=city_url, area_num="{area_num}", page="{page}")
        area_num, plots_dict = 1, dict()
        while True:
            temp_plots_url = plots_url.format(area_num=area_num, page=1)
            common.print_and_sleep('采集{area_num}小区第{page}页: {url}'.format(area_num=area_num, page=1, url=temp_plots_url))
            plots_dict, is_exist = self._get_plots(plots_dict, temp_plots_url)
            if is_exist is False:
                break
            page = 2
            while True:
                temp_plots_url = plots_url.format(area_num=area_num, page=page)
                common.print_and_sleep('采集{area_num}小区第{page}页: {url}'.format(area_num=area_num, page=page, url=temp_plots_url))
                plots_dict, is_exist = self._get_plots(plots_dict, temp_plots_url)
                if is_exist is False:
                    break
                page += 1
            area_num += 1
        operation_file.write_json_file(self.plots_file_name.format(city_name=city_name), plots_dict)

    def _get_plots(self, plots_dict, url):
        '''采集小区列表中的数据
        访问小区列表URL, 并将 HTML 转换为 etree 对象
        获取小区信息的 a 标签, 并从 a 标签中拿出小区名和小区URL, 将这些数据保存到字典类型的变量中
        返回采集到的数据和当前采集URL是否有效
        Args:
            plots_dict: 临时保存的小区信息
            url: 要采集的小区列表url
        return:
            dict 更新后的小区信息
            bool 当前小区url是否有效
        '''
        plots_etree = gather.get_html_to_etree(url, coding=self.coding)
        plots_a_etree = plots_etree.xpath(self.plots_xpath)
        for i in range(0, len(plots_a_etree)):
            plot_name, plot_url = plots_a_etree[i].xpath('text()')[0], plots_a_etree[i].xpath('@href')[0]
            plots_dict[plot_name] = {'plot_name': plot_name, 'plot_url': plot_url}
        return plots_dict, bool(len(plots_a_etree))

    def get_plots_detail(self, file_name):
        plots_dict = operation_file.read_json_file(file_name)
        i = 1
        for key in plots_dict.keys():
            common.print_and_sleep('采集{name}小区详情: {url}'.format(name=key, url=plots_dict[key]['plot_url']))
            plots_dict[key] = self._get_plot_detail(plots_dict[key])
            i += 1
            if i % config.save_file_number == 0:
                common.print_and_sleep('更新文件:{file_name}'.format(file_name=file_name))
                operation_file.write_json_file(file_name, plots_dict)
        common.print_and_sleep('更新文件:{file_name}'.format(file_name=file_name))
        operation_file.write_json_file(file_name, plots_dict)

    def _get_plot_detail(self, plot_dict):
        etree = gather.get_html_to_etree(plot_dict['plot_url'], coding=self.coding)
        plot_dict['地址'] = etree.xpath(self.地址_xpath)[1].split('\r\n')[0]
        plot_dict['地址链'] = '>'.join(etree.xpath(self.地址链_xpath))
        plot_dict.update(zip(etree.xpath(self.详情_keys_xpath), etree.xpath(self.详情_values_xpath)))
        # 经纬度
        plot_html = gather.get_html(plot_dict['plot_url'], coding=self.coding)
        try:
            plot_dict['经纬度'] = ",".join([re.findall(self.经度_re, plot_html)[0], re.findall(self.纬度_re, plot_html)[0]])
        except IndexError:
            plot_dict['经纬度'] = ""
        return plot_dict

    def run(self):
        if os.path.exists(self.citys_file_name) is False:
            self.get_citys()
        for city_key, city_value in operation_file.read_json_file(self.citys_file_name).items():
            if os.path.exists(self.plots_file_name) is False:
                self.get_plots(city_value['city_name'], city_value['city_url'])
                return
        for file_name in os.listdir(self.plots_dir_name):
            self.get_plots_detail(self.plots_dir_name + file_name)
