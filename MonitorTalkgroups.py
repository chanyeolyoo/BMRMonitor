
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

from utils import *

import requests
import os
import sys
import time
import datetime
import random
import json

import threading

from utils import *

####################################################################

class MonitorTalkgroups():
    tg_array = []
    data_array = []
    thread_array = []
    
    is_running = True

    def __init__(self, tgs):
        self.tg_array = tgs
        self.data_array = [{ 'timestamp': time.time(), 'status': '', 'last_active': 0 }] * len(tgs)
        self.thread_array = [[]] * len(tgs)
        
        for i in range(len(tgs)):
            tg = tgs[i]
            t = threading.Thread(target=self._fn_thread, args=(tg['id'], self.data_array, i))
            self.thread_array[i] = t

    def start(self):
        for thread in self.thread_array:
            thread.start()

    def stop(self):
        self.is_running = False
        for thread in self.thread_array:
            thread.join()

    def get(self):
        return self.data_array

    def _fn_thread(self, tgid, data_array, i):
        resp = requests.get('https://hose.brandmeister.network/broker/?group=' + str(tgid), stream=True)
        for line in resp.iter_lines(decode_unicode=True, delimiter='\n\n'):
            if self.is_running == False:
                break
            if line:
                timestamp = time.time()
                # if line.find('ping') == -1 and line.find('+')>=0:
                if line.find('ping') == -1 and len(line) < 100:
                    data_array[i] = { 'timestamp': timestamp, 'status': 'active', 'last_active': timestamp }
                else:
                    data_array[i] = { 'timestamp': timestamp, 'status': 'inactive', 'last_active': data_array[i]['last_active'] }



if __name__ == "__main__":
    import talkgroups
    tgs = talkgroups.tgs

    monitor = MonitorTalkgroups(tgs)
    monitor.start()

    while True:
        print('========================')
        data_array = monitor.get()
        for i in range(len(tgs)):
            tg = tgs[i]
            data = data_array[i]
            print('TG%d: %s (%s)' % (tg['id'], data['status'], get_duration_str(int(time.time()-data['timestamp']))))
        time.sleep(1)

