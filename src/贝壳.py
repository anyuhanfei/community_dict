import os
import re

from utils import operation_file, gather, common
from config import config


class 贝壳:
    '''贝壳网小区信息采集
    '''
    headers = config.universal_headers

    citys_url = "https://www.ke.com/city/"
    plots_url = "https:{domain}/xiaoqu"
    plots_area_url = "https:{domain}{area_url}pg{page}"

    citys_file_name = './temp/贝壳_city.json'
    plots_file_name = './data/贝壳/{city}.json'
    plots_dir_name = './data/贝壳/'

    citys_xpath = '//div[@data-action="Uicode=选择城市_国内"]/div[@class="city_list_section"]/ul[@class="city_list_ul"]/li/div[@class="city_list"]/div/ul/li/a'
    plots_area_url_xpath = '//a[@class=" CLICKDATA"]/@href'
    plots_area_name_xpath = '//a[@class=" CLICKDATA"]/text()'
    plots_xpath = '//a[@class="maidian-detail"]'
    plots_error_xpath = '//div[@class="sec-list-nav clearfix"]'
    地址_xpath = '//div[@class="sub"]/text()'
    地址链_xpath = '//div[@class="fl l-txt"]/a/text()'
    详情_keys_xpath = '//span[@class="xiaoquInfoLabel"]/text()'
    详情_values_xpath = '//span[@class="xiaoquInfoContent"]/text()'
    经纬度_re = "resblockPosition:'(.*?)',"

    def __init__(self):
        pass

    def get_citys(self):
        '''获取城市列表
        访问城市列表 URL, 并将 HTML 转换为 etree 对象
        获取城市信息的 a 标签, 并从 a 标签中拿出城市名和城市 URL, 将这些数据保存到字典类型的变量中
        将数据保存到 JSON 文件中
        '''
        etree = gather.get_html_to_etree(self.citys_url, headers=self.headers)
        citys_etree = etree.xpath(self.citys_xpath)
        citys_dict = dict()
        for city_etree in citys_etree:
            city_name, city_url = city_etree.xpath('text()')[0], city_etree.xpath('@href')[0]
            citys_dict[city_name] = {'city_name': city_name, 'city_url': city_url}
        operation_file.write_json_file(self.citys_file_name, citys_dict)

    def get_plots(self, city_name, city_url):
        '''采集当前城市小区基本数据
        访问当前城市的小区列表(第一页, 但是 url 中无分页标识, 否则获取的区域 url 就会有分页标识)
        判断一下 class 为 sec-list-nav clearfix 的 div 是否存在, 如果存在则说明当前城市没有小区, 直接返回
        获取城市区域的名称及 url
        循环城市区域, 循环页码, 组合小区列表页 url
        访问并将 html 转换为 etree 对象, 并获取小区相关数据标签 etree 对象
        判断当前区域当前页码中是否有小区数据, 如果没有则说明本区域小区数据采集完毕
        若有小区数据则将小区数据暂存在字典中
        所有循环结束, 当前城市小区基本数据采集结束, 保存至 JSON 文件中
        '''
        temp_url = self.plots_url.format(domain=city_url)
        if temp_url.count('.fang.') >= 1:
            print('{city_name}城市无小区列表'.format(city_name=city_name))
            return
        etree = gather.get_html_to_etree(temp_url, headers=self.headers)
        common.print_and_sleep('采集{city_name}小区: {url}'.format(city_name=city_name, url=temp_url))
        if etree.xpath(self.plots_error_xpath) != []:
            print('{city_name}城市无小区列表'.format(city_name=city_name))
            return
        area_dict, plots_dict = dict(), dict()
        area_dict.update(zip(etree.xpath(self.plots_area_name_xpath), etree.xpath(self.plots_area_url_xpath)))
        for area_name, area_url in area_dict.items():
            page = 1
            while page <= 100:
                url = self.plots_area_url.format(domain=city_url, area_url=area_url, page=page)
                common.print_and_sleep('采集{city}城市{area}第{page}页: {url}'.format(city=city_name, area=area_name, page=page, url=url))
                plots_etree = gather.get_html_to_etree(url, headers=self.headers).xpath(self.plots_xpath)
                if plots_etree == []:
                    break
                for plot_etree in plots_etree:
                    plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                    plots_dict[plot_name] = {'plot_name': plot_name, 'plot_url': plot_url}
                page += 1
        print('{city}城市小区列表采集完成'.format(city=city_name))
        operation_file.write_json_file(self.plots_file_name.format(city=city_name), plots_dict)

    def get_plots_detail(self, file_name):
        '''获取当前城市的小区详细信息
        读取小区信息文件, 并循环每个小区信息
        判断此小区是否已采集过详细信息(这里按`地址`这个键来判断), 没有采集则采集详细信息
        每采集20个小区的详细信息则保存一次数据, 小区采集结束后也会保存一次数据
        Args:
            file_name: 单城市的小区信息文件
        '''
        plots_dict = operation_file.read_json_file(file_name)
        i = 1
        for key in plots_dict.keys():
            if plots_dict[key].get('地址') is None:
                common.print_and_sleep('采集{name}小区详情: {url}'.format(name=key, url=plots_dict[key]['plot_url']))
                plots_dict[key] = self._get_plots_detail(plots_dict[key])
                i += 1
            if i % config.save_file_number == 0:
                print('更新文件:{file_name}'.format(file_name=file_name))
                operation_file.write_json_file(file_name, plots_dict)
        if i > 1:
            print('更新文件:{file_name}'.format(file_name=file_name))
            operation_file.write_json_file(file_name, plots_dict)

    def _get_plots_detail(self, plot_dict):
        '''获取当前小区的详细信息
        访问小区的详情URL, 并获取 HTML 及其 etree 对象
        采集地址, 地址链, 经纬度以及其他信息
        将采集的信息整合到旧字典中并返回
        Args:
            plot_dict: 小区的当前信息数据, 包含小区名和小区详情URL
        return:
            dict 小区的最新信息数据
        '''
        html, etree = gather.get_html_and_etree(plot_dict['plot_url'], headers=self.headers)
        try:
            plot_dict['地址'] = etree.xpath(self.地址_xpath)[0]
        except IndexError:
            plot_dict['地址'] = ''
            return plot_dict
        plot_dict['地址链'] = '>'.join(etree.xpath(self.地址链_xpath))
        plot_dict.update(zip(etree.xpath(self.详情_keys_xpath), etree.xpath(self.详情_values_xpath)))
        plot_dict['经纬度'] = re.findall(self.经纬度_re, html)[0]
        for key in plot_dict.keys():
            plot_dict[key] = plot_dict[key].replace(' ', '').replace('\n', '')
        return plot_dict

    def run(self):
        '''执行函数
        第一步: 获取城市列表
        第二步: 获取每个城市的小区基本信息
        第三步: 获取所有小区的详情信息
        '''
        if os.path.exists(self.citys_file_name) is False:
            self.get_citys()
        for city_key, city_value in operation_file.read_json_file(self.citys_file_name).items():
            if os.path.exists(self.plots_file_name.format(city=city_key)) is False:
                self.get_plots(city_value['city_name'], city_value['city_url'])
        for file_name in os.listdir(self.plots_dir_name):
            self.get_plots_detail(self.plots_dir_name + file_name)
