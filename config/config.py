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
# 小区详情获取数量后保存文件
save_file_number = 20


'''
链家
'''
链家_headers = universal_headers

链家_city_list_url = 'https://www.lianjia.com/city/'
链家_plot_list_url = "{city_url}xiaoqu/pg{page}/?from=rec"

链家_city_json_file_name = "./temp/链家_city.json"
链家_plot_json_file_name = "./data/链家/{file_name}小区.json"
链家_plot_json_dir_name = "./data/链家/"

'''
智慧小区
'''
智慧小区_area_list_url = 'https://www.zhihuixiaoqu.com/index/index/xiaoqudaquan?page={page}'
智慧小区_plot_list_url = 'https://www.zhihuixiaoqu.com/index/index/{area_url}&page={page}'
智慧小区_plot_detail_url = 'https://www.zhihuixiaoqu.com/index/index/{plot_url}'

智慧小区_area_json_file_name = "./temp/智慧小区_area.json"
智慧小区_plot_json_file_name = "./data/智慧小区/{area_name}小区.json"


'''
房产超市
'''
房产超市_citys_url = "http://www.fccs.com/"
房产超市_plots_url = "{city_url}/sitemap-xq/search/a{area_num}_p{page}.html"

房产超市_citys_file_name = './temp/房产超市_city.json'
房产超市_plots_file_name = './data/房产超市/{city_name}.json'
房产超市_plots_dir_name = "./data/房产超市/"
