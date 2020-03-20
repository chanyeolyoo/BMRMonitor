
import requests
import os
import sys
import time
import datetime
import json

# "session": "e008d966-4134-4ca4-9d33-a2384c595990",
# "src": 4500342,
# "dst": 45021,
# "start": 1584433829671,
# "last": 1584433829671,
# "ended": 1584433830533

# "count": 1,
# "results": [
# {
#     "callsign": "VK2FAED",
#     "city": "Sydney",
#     "country": "Australia",
#     "fname": "Chanyeol",
#     "id": 5050905,
#     "remarks": "DMR",
#     "state": "New South Wales",
#     "surname": "Yoo"
# }
# ]

def get_duration_str(second_dur):
    delta = datetime.timedelta(seconds=round(second_dur, 1))
    return str(delta)

def get_datetime_str(unix_time):
    text = datetime.datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
    return text

def get_radio_info(rid):
    r = requests.get('https://www.radioid.net/api/dmr/user/?id=' + str(rid)) 
    data = r.json()

    radio_info = data['results'][0]
    radio_label = '%s (%s %s, %s)' % (radio_info['callsign'], radio_info['fname'], radio_info['surname'], radio_info['country'])

    return radio_info, radio_label
    


def get_last_heard(tg):
    r = requests.get('https://hose.brandmeister.network/api/heard/?id=' + str(tg)) 
    data = r.json()
    latest = data[00]

    try:
        # start_time = datetime.datetime.fromtimestamp(int(latest['start']/1000)).strftime('%Y-%m-%d %H:%M:%S')
        start_time = latest['start']
    except:
        start_time = 0

    try:
        # last_time = datetime.datetime.fromtimestamp(int(latest['last']/1000)).strftime('%Y-%m-%d %H:%M:%S')
        last_time = latest['last']
    except:
        last_time = 0

    try:
        # end_time = datetime.datetime.fromtimestamp(int(latest['ended']/1000)).strftime('%Y-%m-%d %H:%M:%S')
        end_time = latest['ended']
    except:
        end_time = last_time

    src = latest['src']
    dst = latest['dst']

    radio_info = { 'callsign': 'TEST', 'id': src }

    st = { 'radio_info': radio_info, 'tg': dst, 'start_time': get_datetime(start_time), 'last_time': get_datetime(last_time), 'end_time': get_datetime(end_time), 'elapsed_time': (time.time() - end_time/1000)}
    return st

if __name__ == "__main__":
    data = get_last_heard(310997)
    print(data)

# # print(start, ': ', src, ' -> ', dst)
# lastheard = get_last_heard(2501)
# radio_info, radio_label = get_radio_info(5050905)
# print(lastheard)
# print(radio_info)
# print(radio_label)

# a = 1