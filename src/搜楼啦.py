import os

from utils import operation_file, common, gather
from config import config


class 搜楼啦:
    ''''''
    citys_url = "http://www.souloula.com/"
    plots_url = "{city_domain}/xiaoqu/list_{page}.html"

    citys_file_name = "./temp/搜楼啦_city.json"
    plots_file_name = "./data/搜楼啦/{city_name}.json"

    citys_xpath = '//div[@class="ir"]/a'
    plots_xpath = '//div[@class="ni"]/a[1]'
    plots_error_xpath = '//div[@class="zhuan"]'

    def __init__(self):
        pass

    def get_citys(self):
        ''''''
        common.print_and_sleep('采集搜楼啦城市信息: {url}'.format(url=self.citys_url))
        citys_etree = gather.get_html_to_etree(self.citys_url)
        citys_dict = dict()
        for city_etree in citys_etree.xpath(self.citys_xpath):
            city_name, city_url = city_etree.xpath('text()')[0], city_etree.xpath('@href')[0]
            citys_dict[city_name] = {'city_name': city_name, 'city_url': city_url}
        operation_file.write_json_file(self.citys_file_name, citys_dict)

    def get_plots(self, city_name, plots_url):
        page, plots_dict = 1, dict()
        while True:
            temp_plots_url = plots_url.format(page=page)
            common.print_and_sleep('{city_name}城市小区采集第{page}页: {url}'.format(city_name=city_name, page=page, url=temp_plots_url))
            plots_etree = gather.get_html_to_etree(temp_plots_url)
            if len(plots_etree.xpath(self.plots_error_xpath)) >= 1:
                plots_file_name = self.plots_file_name.format(city_name=city_name)
                common.print_and_sleep('{city_name}城市小区采集结束,保存数据至{file_name}'.format(city_name=city_name, file_name=plots_file_name))
                operation_file.write_json_file(plots_file_name, plots_dict)
                break
            for plot_etree in plots_etree.xpath(self.plots_xpath):
                plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                plots_dict[plot_name] = {'plot_name': plot_name, 'plot_url': plot_url}
            page += 1

    def run(self):
        if os.path.exists(self.citys_file_name) is False:
            self.get_citys()
        for city_key, city_value in operation_file.read_json_file(self.citys_file_name).items():
            if os.path.exists(self.plots_file_name.format(city_name=city_value['city_name'])) is False:
                self.get_plots(city_value['city_name'], self.plots_url.format(city_domain=city_value['city_url'], page="{page}"))
                break
