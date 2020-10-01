import time

from config.config import time_interval


def print_and_sleep(*args, time_interval=time_interval):
    '''打印内容后休眠一定时间
    '''
    print(*args)
    time.sleep(time_interval)
