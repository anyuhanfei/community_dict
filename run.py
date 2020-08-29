'''
按顺序爬取数据, 无效率要求
'''
from src import 链家, 房产超市

'''链家'''
obj = 链家.链家()
obj.run()

'''房产超市'''
obj = 房产超市.房产超市()
obj.run()
