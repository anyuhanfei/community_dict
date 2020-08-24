import os
import time

from config import config
from utils import gather, operation_file


class 智慧小区:
    area_list_url = config.智慧小区_area_list_url
    plot_list_url = config.智慧小区_plot_list_url

    area_list_xpath = '//span[@class="layui-col-xs6 layui-col-sm6 layui-col-md3"]/a'
    plot_list_xpath = '//span[@class="layui-col-xs6 layui-col-sm6 layui-col-md3"]/a'

    def __init__(self):
        pass

    def get_areas(self):
        if os.path.exists(config.智慧小区_area_json_file_name) is True:
            return
        page, area_dict = 1, dict()
        while True:
            area_list_url = self.area_list_url.format(page=page)
            print('开始采集: {}'.format(area_list_url))
            areas_etree = gather.get_html_to_etree(area_list_url, headers=config.universal_headers)
            area_list_etree = areas_etree.xpath(self.area_list_xpath)
            if len(area_list_etree) <= 0:
                break
            for area_etree in area_list_etree:
                area_name, area_url = area_etree.xpath('text()')[0][:-4], area_etree.xpath('@href')[0]
                area_dict[area_name] = {'area_name': area_name, 'area_url': self.plot_list_url.format(area_url=area_url, page="{page}")}
            page += 1
            time.sleep(config.time_interval)
            break
        operation_file.write_json_file(config.智慧小区_area_json_file_name, area_dict)

    def get_plots(self):
        area_dict = operation_file.read_json_file(config.智慧小区_area_json_file_name)
        for key, area in area_dict.items():
            area_name, area_url = area['area_name'], area['area_url']
            if os.path.exists(config.智慧小区_plot_json_file_name.format(area_name=area_name)) is True:
                print('区域已采集:{url}'.format(url=area_url))
                continue

            page, plot_dict = 1, dict()
            while True:
                temp_area_url = area_url.format(page=page)
                print('开始采集: {}'.format(temp_area_url))
                plots_etree = gather.get_html_to_etree(temp_area_url, headers=config.universal_headers)
                plot_list_etree = plots_etree.xpath(self.plot_list_xpath)
                if len(plot_list_etree) <= 0:
                    break
                for plot_etree in plot_list_etree:
                    plot_name, plot_url = plot_etree.xpath('text()')[0], plot_etree.xpath('@href')[0]
                    plot_dict[plot_name] = {'plot_name': plot_name, 'plot_url': config.智慧小区_plot_detail_url.format(plot_url=plot_url, page="{page}")}
                page += 1
                time.sleep(config.time_interval)
                break
            operation_file.write_json_file(config.智慧小区_plot_json_file_name.format(area_name=area_name), plot_dict)

    def run(self):
        self.get_areas()
        self.get_plots()
