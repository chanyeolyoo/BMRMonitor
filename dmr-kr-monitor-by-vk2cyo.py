"""
Brandmeister DMR Monitor for Korean Talkgroups

Author: Chanyeol Yoo (VK2CYO)
Copyright: Chanyeol Yoo, Ph.D. (VK2CYO), 2020
License: MIT
Version: v1.1
Maintainer: Chanyeol Yoo (VK2CYO)
Email: vk2cyo@gmail.com
"""

import asyncio
import websockets
import os
import datetime, time
import sys
import requests
from colorama import Fore, Back, Style, init

ver = 1.1
IS_TEST = False

tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]  # TALKGROUPS TO BE MONITORED
NUM_HISTORY = 5     # NUMBER OF HISTORY FOR EACH TALKGROUP
TIMEOUT = 180       # TIMEOUT FOR INACTIVE CALLS

NUM_PADD = 30       # NUMBER OF EMPTY SPACES IN ACTIVE CALL FIELD

init(autoreset=True)
CHAR_BOLD = '\033[1m'
CHAR_UNBOLD = '\033[0m'
CHAR_RESET = Back.RESET + Fore.RESET + Style.RESET_ALL + CHAR_UNBOLD

STYLE_ACTIVE = Back.RED  + Fore.BLACK
STYLE_INACTIVE = Back.YELLOW + Fore.BLACK
STYLE_RESET = Back.RESET + Fore.RESET + Style.RESET_ALL + CHAR_UNBOLD

#### CHECKING FOR UPDATE
try:
    text_release = requests.get('https://api.github.com/repos/chanyeolyoo/BMRMonitor/releases/latest').text
    text_release = text_release.replace('false', 'False')
    text_release = text_release.replace('true', 'True')
    text_release = text_release.replace('null', 'None')
    resp_release = eval(text_release)
    tag_release = float(resp_release['tag_name'])

    if (tag_release > ver) or (tag_release >= ver and IS_TEST):
        is_update_available = True
    else:
        is_update_available = False
except:
    is_update_available = False

#### INITIALISING HISTORY LIST FOR EACH TALKGROUP
history_tgs = {}
for tg in tgs:
    history_tgs[tg] = []

"""
SORT_DATA_BY_TIME
    - This function updates "history_tgs" list given new data
    - It maintains NUM_HISTORY number of calls for each talkgroup
    - If duplicate callsigns are present, only the latest one remains
    - Returned "history_tgs" is in descending order of call time
    -- If the call is active, then it looks at START time
    -- Otherwise, it looks at STOP time
"""
def sort_data_by_time(data):
    now = time.time()


    data_new = []
    callsigns = set([d['SourceCall'] for d in data])
    for callsign in callsigns:
        entry = {}
        for d in data:
            if d['SourceCall'] == callsign:
                if (len(entry) == 0) or (d['Stop'] > entry['Stop']) or (d['Stop']==0 and d['Start'] > entry['Start']):
                    entry = d
        data_new.append(entry)

    data = data_new
    data_new = []
    for d in data:
        if d['Stop'] == 0 or now-d['Stop'] < TIMEOUT:
            data_new.append(d)

    data_new = sorted(data_new, key=lambda k:k['Start'], reverse=True)
    data_new = data_new[0:(NUM_HISTORY)]
    return data_new

"""
GET_DATA_FROM_PACKET
    - This function converts string from websocket to dict format
    - Returns dict data if string is valid; otherwise returns None
"""
def get_data_from_packet(str):
    str = str.replace('\\', '')
    str = str.replace('"{', '{')
    str = str.replace('}"', '}')
    str = str.replace('null', 'None')
    str = str[str.find('{'):str.rfind('}')+1]
    try:
        data = eval(str)
        return data['payload']
    except:
        return None

"""
PRINT_HISTORY
    - Prints "history_tgs" in terminal
"""
def print_history(history_tgs):
    now = time.time()

    if sys.platform == 'linux':
        os.system('clear')
    else:
        os.system('cls')

    if IS_TEST:
        print('***** TEST VERSION *****')

    for tg in tgs:
        text_tg = text_tg = '%s %-5d %s' % (STYLE_RESET, tg, STYLE_RESET)
        text_active = ''
        text_inactive = ''

        history_tg = history_tgs[tg]
        try:
            text_inactive = ''
            for d in history_tg:
                if now - d['Stop'] < TIMEOUT:
                    text_inactive = text_inactive + ('%s (%ds), ' % (d['SourceCall'], now - d['Stop']))
            text_inactive = text_inactive

            if history_tg[0]['Stop'] == 0:
                elapsed = now-history_tg[0]['Start']
                text_active = '%s, %s (%ds) ' % (history_tg[0]['SourceCall'], history_tg[0]['SourceName'], elapsed)
                text_active = text_active.ljust(NUM_PADD, '-')
                text_tg = '%s %-5d %s' % (STYLE_ACTIVE, tg, STYLE_RESET)
            else:
                if len(text_inactive) > 0:
                    text_active = ''.ljust(NUM_PADD, '-')
                    text_tg = '%s %-5d %s' % (STYLE_INACTIVE, tg, STYLE_RESET)
        except Exception as e:
            a = 1

        print('%s | %s | %s' % (text_tg, text_active.ljust(NUM_PADD), text_inactive))

    print('Developed by Chanyeol Yoo (VK2CYO) v%.1f' % ver)
    print('https://github.com/chanyeolyoo/BMRMonitor')

    if is_update_available:
        print(Back.GREEN + Fore.BLACK + 'Update available: ' + resp_release['html_url'] + Style.RESET_ALL)
    else:
        print('Up-to-date')

"""
ASYNC_FETCH
    - Connects to Brandmeister Last Heard using websockets
    - Raw string is added to "queue"
    - Only those calls made to talkgroups in "tgs" are put in the queue
"""
async def async_fetch(queue):
    uri = "wss://api.brandmeister.network/lh/%7D/?EIO=3&transport=websocket"
    while True:
        async with websockets.connect(uri) as websocket:
            try:
                while True:
                    str = await websocket.recv()
                    await queue.put(str)
                    # print(queue.qsize())

            except Exception as e:
                print('RESTART: ' + e.__str__())
            
"""
ASYNC_PROCESS
    - Waits for queue data
    - When there is string data in "queue", it calls "sort_data_by_time" function
    - Prints to terminal every one second
"""
async def async_process(queue):
    last_print = time.time()
    while True:
        str = await queue.get()
        data = get_data_from_packet(str)
        if data==None:
            continue

        if data['DestinationID'] in tgs:
            dstID = data['DestinationID']
            history_tgs[dstID] = sort_data_by_time(history_tgs[dstID] + [data])

        #### THIS PART TO BE TAKEN OUT TO SEPARATE FUNCTION
        if time.time() - last_print >= 1:
            print_history(history_tgs)
            last_print = time.time()
            

"""
Starts main loop
"""
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    afetch = async_fetch(queue)
    aprocess = async_process(queue)

    loop.run_until_complete(asyncio.gather(afetch, aprocess))
    loop.close()
