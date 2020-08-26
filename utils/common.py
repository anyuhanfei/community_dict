import time

from config.config import time_interval


def print_and_sleep(*args, **kwargs):
    '''打印内容后休眠一定时间
    '''
    print(*args, **kwargs)
    time.sleep(time_interval)
