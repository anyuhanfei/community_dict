import os
import re

from utils import operation_file, gather, common
from config import config


class 贝壳:
    citys_url = "https://www.ke.com/city/"

    citys_file_name = './temp/贝壳_city.json'

    citys_xpath = '//ul[@class="city_list_ul"]/li/div[@class="city_list"]/div/ul/li'

    def __init__(self):
        pass

    def run(self):
        pass
