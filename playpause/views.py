# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from pymongo import MongoClient
from collections import Counter
# import logging

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

    if date_search == '':
        return HttpResponse("错误！！</br>日期为空")
    if start == '' or end == '':
        start = "12:30:00"
        end = "14:00:00"

    start_search = date_search+"T"+start+"Z"
    end_search = date_search+"T"+end+"Z"
    # return HttpResponse(start_search)

    client = MongoClient('mongodb://localhost:27017')
    # client = MongoClient('mongodb://120.26.4.97:30000')
    db = client.report

    docs = db.playpause.find(
        {'inserttime': {'$gte':start_search, '$lte':end_search}, 'playpause.header.live': True},
        projection = {'_id': False, 'playpause.header': True, 'playpause.content':True}
    )
    # return HttpResponse(docs)

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
