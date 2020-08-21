from config import headers


# 全局配置


# 安居客配置
安居客城市列表url = "https://www.anjuke.com/yaan/cm/p5/"
安居客小区列表url = "https://www.anjuke.com/{city}/cm/p{page}/"

安居客_小区列表最大页码 = 34
安居客_headers = headers.安居客_headers
安居客_cookies = headers.安居客_cookies

安居客城市列表文件 = './temp/安居客_城市列表.json'
安居客小区列表文件 = './temp/安居客_{city}小区列表.json'
