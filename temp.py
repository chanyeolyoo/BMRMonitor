
import datetime, time

tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]

NUM_HISTORY = 50

def sort_data_by_time(data):
    data_new = []
    callsigns = set([d['SourceCall'] for d in data])
    for callsign in callsigns:
        entry = {}
        for d in data:
            if d['SourceCall'] == callsign:
                if entry.__len__() == 0 or d['Start'] > entry['Start']:
                    entry = d
        data_new.append(entry)

    data_new = sorted(data_new, key=lambda k:k['Start'], reverse=True)
    data_new = data_new[0:(NUM_HISTORY)]
    return data_new

now = time.time()

history = {}
for tg in tgs:
    history[tg] = []

history[450] = [{'DestinationID': 450, 'SourceCall': 'callsign1', 'Start': now-100, 'End': now-80}]


data = []
data.append({'DestinationID': 450, 'SourceCall': 'callsign3', 'Start': now-50, 'End': now-40})
data.append({'DestinationID': 450, 'SourceCall': 'callsign4', 'Start': now-30, 'End': now-20})
data.append({'DestinationID': 450, 'SourceCall': 'callsign2', 'Start': now-70, 'End': now-60})
data.append({'DestinationID': 450, 'SourceCall': 'callsign5', 'Start': now-20, 'End': now-15})
data.append({'DestinationID': 450, 'SourceCall': 'callsign2', 'Start': now-10, 'End': now-8})
data.append({'DestinationID': 450, 'SourceCall': 'callsign3', 'Start': now-5, 'End': now-2})

print(data)

data = sort_data_by_time(history[450] + data)
print(data)

a = 1
