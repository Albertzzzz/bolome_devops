# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from pymongo import MongoClient
from collections import Counter, defaultdict
# import logging
from .common_func import get_cdn_name, get_ip_info

# Create your views here.
def index(request):
    return render(request, 'playpause/index.html')

def pause_count_distribution(request):
    if 'date_search' in request.GET:
        date_search = request.GET['date_search']
    else:
        return render(request, 'playpause/error.html')
    if 'start' in request.GET and 'end' in request.GET:
        start = request.GET['start']
        end = request.GET['end']
    else:
        return render(request, 'playpause/error.html')
    if 'playpause' in request.GET:
        playpause = request.GET['playpause']
    else:
        return render(request, 'playpause/error.html')

    if date_search == '':
        return HttpResponse("错误！！</br>日期为空")
#     if start == '' or end == '':
        # start = "12:30:00"
        # end = "14:00:00"
    start_search = date_search+"T"+start+"Z"
    end_search = date_search+"T"+end+"Z"
    # return HttpResponse(start_search)

    client = MongoClient('mongodb://localhost:27017')
    # client = MongoClient('mongodb://120.26.4.97:30000')
    db = client.report

    docs = db.playpause.find(
        {'inserttime': {'$gte':start_search, '$lte':end_search}, 'playpause.header.live': True},
        projection = {'_id': False, 'playpause.header': True, 'playpause.content':True, 'inserttime': True}
    )
    # return HttpResponse(docs)

    if playpause == 'playpause_analysis':
        total_pause = 0
        cnt_device = Counter()
        cnt_cdnip = Counter()
        cdnip2selfip = defaultdict(list)
        cdnip2url = defaultdict(list)

        for doc in docs:
            url = doc['playpause']['header']['url']
            playertype = doc['playpause']['header']['playertype']
            cdnip = doc['playpause']['content']['cdnip']
            selfip = doc['playpause']['content']['selfip']
            dns = doc['playpause']['content']['dns']

            total_pause += 1
            cnt_device[playertype] += 1
            cnt_cdnip[cdnip] += 1
            cdnip2url[cdnip].append(url)
            cdnip2selfip[cdnip].append([selfip, dns])

        cdnip_info_all = []
        for cdnip_info in cnt_cdnip.most_common():
            tmp = ''
            for url_info in cdnip2url[cdnip_info[0]]:
                tmp = url_info
            cnt_selfip = Counter()
            selfip_dns = {}
            selfip_info_all =[]
            for selfip, dns in cdnip2selfip[cdnip_info[0]]:
                cnt_selfip[selfip] += 1
                if dns != '':
                    selfip_dns[selfip] = dns
            for selfip_info in cnt_selfip.most_common():
                dns_ip = ''
                try:
                    dns_ip =selfip_dns[selfip_info[0]]
                except KeyError:
                    dns_ip = 'No DNS info'
                selfip_info_all.append([get_ip_info(selfip_info[0]), selfip_info[1], get_ip_info(dns_ip)])


            cdnip_info = [get_ip_info(cdnip_info[0]), get_cdn_name(tmp), cdnip_info[1], selfip_info_all]

            cdnip_info_all.append(cdnip_info)


        return render(request, 'playpause/playpause_analysis.html', {'total_pause': total_pause, 'cnt_device': cnt_device.most_common(), 'cnt_cdnip': cdnip_info_all})

    elif playpause == 'pause_count_distribution':
        pause_tourid = Counter()
        total_pause = 0

        for doc in docs:
            tourid = doc['playpause']['header']['tourid']
            total_pause += 1
            pause_tourid[tourid] += 1

        pause_distribution = Counter()
        for pause_info in pause_tourid.most_common():
            tmp = pause_info[1]
            pause_distribution[tmp] += 1

        distribution_info_all = []
        for distribution_info in sorted(pause_distribution.most_common()):
            percentage = round((float(distribution_info[0] * distribution_info[1])*100 /total_pause),2)
            tmp_data = [distribution_info[0], distribution_info[1], percentage]
            distribution_info_all.append(tmp_data)

        return render(request, "playpause/pause_count_distribution.html", {'distribution_info_all': distribution_info_all})
    elif playpause == 'pause_mins_distribution':
        # return HttpResponse(playpause)
        pause_mins = Counter()
        pause_mins_all = []
        for doc in docs:
            inserttime = doc['inserttime']
            pause_mins[inserttime[:16]] += 1
        for mins_info in sorted(pause_mins.most_common()):
            pause_mins_all.append([mins_info[0], mins_info[1]])

        return render(request, 'playpause/pause_mins_distribution.html', {'pause_mins_all': pause_mins_all})
