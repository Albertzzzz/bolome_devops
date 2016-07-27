# -*- coding: utf-8 -*-
import sys
import re
import os
from ipip import IPX
reload(sys)
sys.setdefaultencoding('utf-8')


def get_cdn_name(url):
    if('ws' in url):
        return '网宿'
    elif('gs' in url):
        return '高升'
    elif('uc' in url):
        return 'UC'
    elif('bs' in url):
        return '白山'
    else:
        return 'CDN is not defined'

def get_ip_info(ip_addr):
    info = ''
    if(re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip_addr) != None):
        if (ip_addr == '203.156.235.250'):
            info = '203.156.235.250(波罗蜜全球购本部)'
        else:
            ip_info = IPX.find(ip_addr)
            if ip_info != 'N/A':
                ip_info_list = ip_info.split("\t")
                info = '{}({} {} {})'.format(ip_addr, ip_info_list[1], ip_info_list[2], ip_info_list[4])
    elif ip_addr == 'No DNS info':
        info = 'No DNS info'
    else:
        info = "ip format is invalid"
    return info

IPX.load(os.path.abspath("/usr/local/lib/python2.7/dist-packages/mydata4vipday2.datx"))
