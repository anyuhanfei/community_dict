import os
import math

from config import config
from utils import gather, operation_file, common


class 链家:
    '''采集链家网的小区数据'''
    citys_url = 'https://www.lianjia.com/city/'
    plots_url = '{city_url}xiaoqu/pg{page}/?from=rec'

    headers = config.universal_headers

    city_list_xpath = '//div[@class="city_province"]/ul/li/a'  # 城市列表xpath
    page_maximum_xpath = '//h2[@class="total fl"]/span/text()'  # 小区列表最大页码xpath
    plot_list_xpath = '//div[@class="info"]/div[@class="title"]/a'  # 小区列表xpath
    plot_detail_address_xpath = '//div[@class="detailDesc"]/text()'  # 小区详情地址xpath
    plot_detail_area_xpath = '//div[@class="fl l-txt"]/a/text()'  # 小区详情地址链xpath
    plot_detail_nautica_xpath = '//span[@class="actshowMap"]/@mendian'  # 小区经纬度xpath
    plot_detail_other_keys_xpath = '//span[@class="xiaoquInfoLabel"]/text()'  # 小区其他详情数据的键xpath
    plot_detail_other_values_xpath = '//span[@class="xiaoquInfoContent"]/text()'  # 小区其他详情数据的值xpath

    citys_file_name = "./temp/链家_city.json"
    plots_file_name = "./data/链家/{file_name}小区.json"
    plots_dir_name = "./data/链家/"

    continue_city_name_list = ['滁州', '秦皇岛', '保亭', '澄迈', '儋州', '临高', '乐东', '陵水', '琼海', '五指山', '文昌', '万宁', '三门峡', '宜昌', '海门', '昆山', '徐州', '长春', '包头', '菏泽', '济宁', '泰安', '德阳', '巴中', '广元', '乐山', '眉山', '南充', '遂宁', '西安', '晋中', '乌鲁木齐', '大理', '西双版纳', '嘉兴', '衢州', '义乌']

    def __init__(self):
        pass

    def get_citys(self):
        '''获取城市列表
        访问城市列表 URL 并将得到的 HTML 转换为 etree 对象
        从 etree 对象中得到城市信息所在的 a 标签
        从 a 标签中取出城市名和城市对应的 URL, 保存至 JSON 文件中
        '''
        city_etree = gather.get_html_to_etree(self.citys_url, headers=self.headers)
        citys = dict()
        for city in city_etree.xpath(self.city_list_xpath):
            city_name, city_url = city.xpath('text()')[0], self.plots_url.format(city_url=city.xpath('@href')[0], page="{page}")
            citys[city_name] = {'city_name': city_name, 'city_url': city_url}
        operation_file.write_json_file(self.citys_file_name, citys)

    def get_all_city_plots(self):
        '''获取所有城市的小区
        读取城市列表 JSON 文件, 获取全部城市列表(字典类型)
        循环城市列表, 获取城市名和对应的 URL, 当前获取的 URL 与展示小区列表的 URL 不同
        判断当前城市小区的 JSON 文件是否存在, 如果存在则说明此城市已完成采集, 跳过当前城市
        通过判断则采集当前城市小区数据
        '''
        for city_key, city_value in operation_file.read_json_file(self.citys_file_name).items():
            if os.path.exists(self.plots_file_name.format(file_name=city_value['city_name'])) is True or self.continue_city_name_list.count(city_value['city_name']) >= 1:
                continue
            self._get_plots(city_value['city_name'], city_value['city_url'])

    def _get_plots(self, city_name, city_url):
        '''获取城市中的小区
        初始化当前页码, 最大页码, 使其能通过循环的判定, 以进行第一次循环
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
        page_maximum, page, plot_dict = 1, 1, dict()
        while page <= page_maximum:
            plot_url = city_url.format(page=page)
            common.print_and_sleep('开始采集：{url}'.format(url=plot_url))
            plot_etree = gather.get_html_to_etree(plot_url, headers=self.headers)
            # 获取最大页码
            if page_maximum == 1 and page == 1:
                try:
                    page_maximum = math.ceil(int(plot_etree.xpath(self.page_maximum_xpath)[0]) / 30)
                except BaseException:
                    print('获取最大页码异常, 跳过当前城市: {city_name}'.format(city_name=city_name))
                    return
            # 获取小区名称及url
            for plot_etree in plot_etree.xpath(self.plot_list_xpath):
                plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                plot_dict[plot_name] = {'plot_name': plot_name, 'plot_url': plot_url}
            # 下次循环的准备
            page += 1
        # 将数据保存至文件中
        common.print_and_sleep('{city_name}采集结束,保存数据'.format(city_name=city_name))
        operation_file.write_json_file(self.plots_file_name.format(file_name=city_name), plot_dict)

    def get_all_plot_detail(self):
        # 读取链家目录下全部文件
        # 读取每个文件中的 json 数据
        # 判断每个小区数据, 如果没有详细数据则获取
        # 每获取 100 个小区数据或者本文件读取结束, 保存
        for plot_file in os.listdir(self.plots_dir_name):
            plot_file_name = self.plots_dir_name + plot_file
            plots_dict = operation_file.read_json_file(plot_file_name)
            i = 1
            for plot_key in plots_dict.keys():
                if plots_dict[plot_key].get('地址') is None:
                    plots_dict[plot_key] = self._get_plot_detail(plots_dict[plot_key])
                    i += 1
                if i % config.save_file_number == 0:
                    print('更新文件: {file_name}'.format(file_name=plot_file_name))
                    operation_file.write_json_file(plot_file_name, plots_dict)
            print('更新文件: {file_name}'.format(file_name=plot_file_name))
            operation_file.write_json_file(plot_file_name, plots_dict)

    def _get_plot_detail(self, plot_dict):
        '''获取小区的详细数据
        访问小区字典中的小区详情 URL, 并将得到的 HTML 转换为 etree 对象
        获取所有详情数据, 地址, 经纬度等等
        Args:
            plot_dict: 小区信息字典, 当前仅有小区名称及小区详情页URL
        return:
            dict, 小区完整信息字典
        '''
        common.print_and_sleep('采集{name}小区详情:{url}'.format(name=plot_dict['plot_name'], url=plot_dict['plot_url']))
        etree = gather.get_html_to_etree(plot_dict['plot_url'], headers=self.headers)
        try:
            plot_dict['地址'] = etree.xpath(self.plot_detail_address_xpath)[0]
        except BaseException:
            plot_dict['地址'] = ''
            return plot_dict
        plot_dict['地址链'] = '>'.join(etree.xpath(self.plot_detail_area_xpath))
        try:
            plot_dict['经纬度'] = etree.xpath(self.plot_detail_nautica_xpath)[0]
        except IndexError:
            plot_dict['经纬度'] = ''
        plot_dict.update(zip(etree.xpath(self.plot_detail_other_keys_xpath), etree.xpath(self.plot_detail_other_values_xpath)))
        return plot_dict

    def run(self):
        '''执行函数
        第一步: 采集城市列表
        第二步: 采集城市小区的基本数据
        第三步: 采集小区的详细数据
        '''
        if os.path.exists(self.citys_file_name) is False:
            self.get_citys()
        self.get_all_city_plots()
        self.get_all_plot_detail()
