#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import random
import csv
import operator
import urllib3
import sys

# 禁用安全请求警告
urllib3.disable_warnings()

URL = "https://www.watchguard.com/wgrd-products/appliances-compare"
HEADERS = ["Model", "Firewall Throughput", "VPN Throughput", "AV Throughput", "IPS Throughput", "UTM Throughput"]


def get_compare_url(product_info):
    '''
    随机抽取3个产品对比，返回产品名称和比较页面的url
    :param product_info: 所有产品信息
    :return: （名称list，url）
    '''
    compare_info = random.sample(product_info, 3)
    name_list = []
    id_list = []
    for i in compare_info:
        name_list.append(i.keys()[0].split()[-1])
        id_list.append(i.values()[0])
    return name_list, URL+'/'+'/'.join(id_list)


def get_product_info():
    '''
    获取需要对比的M/T系列产品信息
    :return: 产品信息
    '''
    req = requests.get(URL, verify=False)
    soup = BeautifulSoup(req.content, 'html.parser')
    product_list = soup.findAll("optgroup")

    firebox_m_series = [{i.string: i.get('value')} for i in product_list[0].findAll("option")]
    firebox_t_series = [{i.string: i.get('value')} for i in product_list[1].findAll("option")]
    firebox_t_series[0:0] = firebox_m_series
    return firebox_t_series


def get_performance_data(name_list,url):
    '''
    返回请过处理后可以字节写入文件的性能数据
    :param name_list: 产品名称列表
    :param url: 对比页面url
    :return: 性能数据list
    '''
    req = requests.get(url, verify=False)
    compare_soup = BeautifulSoup(req.content, 'html.parser')
    performance_tag_list = [td for td in compare_soup.select('td[class=""]')
                           if "Firewall Throughput " == td.string or "VPN Throughput " == td.string
                           or "AV Throughput " == td.string or "IPS Throughput " == td.string
                           or "UTM Throughput " == td.string]
    firewall = filter(None, [i.string.replace("\n", "").replace(" ", "") for i in performance_tag_list[0].next_siblings])
    vpn = filter(None, [i.string.replace("\n", "").replace(" ", "") for i in performance_tag_list[1].next_siblings])
    av = filter(None, [i.string.replace("\n", "").replace(" ", "") for i in performance_tag_list[2].next_siblings])
    ips = filter(None, [i.string.replace("\n", "").replace(" ", "") for i in performance_tag_list[3].next_siblings])
    utm = filter(None, [i.string.replace("\n", "").replace(" ", "") for i in performance_tag_list[4].next_siblings])
    data = map(list, zip(firewall, vpn, av, ips, utm))
    [data[name_list.index(name)].insert(0, name) for name in name_list]
    for i in data:
        if "Gbps" in i[1]:
            i[1] = float(i[1].rstrip("Gbps"))
        elif "Mbps" in i[1]:
            i[1] = float(i[1].rstrip("Mbps"))/1000
        data.sort(key=operator.itemgetter(1))
    for i in data:
        if i[1] >= 1:
            i[1] = str(i[1])+"Gbps"
        else:
            i[1] = str(int(i[1]*1000))+"Mbps"
    return data


def main(csv_file):
    name_list, compare_url = get_compare_url(get_product_info())
    print("Comparison_url is: %s" % compare_url)
    data = get_performance_data(name_list, compare_url)
    data[0:0] = [HEADERS]
    with open("./"+csv_file, "wb") as f:
        csv.writer(f).writerows(data)

if __name__ == '__main__':
    if not sys.argv[1].endswith(".csv"):
        print("Please enter a string ending with .csv")
        exit(1)
    main(sys.argv[1])
