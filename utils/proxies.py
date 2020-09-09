'''
采集代理
'''
import telnetlib

from utils import gather


def get_proxies():
    url, proxies = "https://www.kuaidaili.com/free/inha/{page}/", []

    for i in range(1, 4):
        etree = gather.get_html_to_etree(url.format(page=i))
        ips, ports = etree.xpath('//td[@data-title="IP"]/text()'), etree.xpath('//td[@data-title="PORT"]/text()')
        for i in range(0, len(ips)):
            try:
                print('检测{ip}:{port}'.format(ip=ips[i], port=ports[i]))
                telnetlib.Telnet(ips[i], port=ports[i], timeout=5)
            except BaseException:
                print('{ip}:{port}超时'.format(ip=ips[i], port=ports[i]))
            else:
                proxie = {
                    'http': 'http://{ip}:{port}'.format(ip=ips[i], port=ports[i]),
                    'https': 'http://{ip}:{port}'.format(ip=ips[i], port=ports[i]),
                }
                proxies.append(proxie)
    return proxies
