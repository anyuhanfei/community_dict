'''
按顺序爬取数据, 无效率要求
'''
import multiprocessing

from src import 房产超市, 链家, 搜楼啦, 贝壳

# '''房产超市'''
# obj = 房产超市.房产超市()
# obj.run()

# '''链家'''
# obj = 链家.链家()
# obj.run()

# '''搜楼啦'''
# obj = 搜楼啦.搜楼啦()
# obj.run()

# '''贝壳'''
# obj = 贝壳.贝壳()
# obj.run()


def worker(obj):
    obj.run()


obj_list = [房产超市.房产超市(), 链家.链家(), 搜楼啦.搜楼啦(), 贝壳.贝壳()]
jobs = []
for i in range(0, len(obj_list)):
    p = multiprocessing.Process(target=worker, args=(obj_list[i],))
    jobs.append(p)
    p.start()

while True:
    res = input('退出请输入out:')
    if res == 'out':
        break
