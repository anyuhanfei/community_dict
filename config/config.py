# from config import headers


'''
全局配置
'''

# 通用headers
universal_headers = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}
# 最终数据保存名称
plot_file_name = "./data/{domain}/{city}小区.json"
# 每次采集时间间隔
time_interval = 5


'''
链家配置

先采集所有的城市信息， 再采集每个城市的小区的基本信息（小区名和详情页的url），最后采集小区的详情信息
'''
链家_headers = universal_headers

链家_city_list_url = 'https://www.lianjia.com/city/'
链家_plot_list_url = "{city_url}xiaoqu/pg{page}/?from=rec"

链家_city_json_file_name = "./temp/链家_city.json"
链家_plot_json_file_name = "./data/链家/{file_name}小区.json"
