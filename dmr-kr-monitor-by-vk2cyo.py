
import asyncio
import websockets
import os
import datetime, time
import sys
import requests
from colorama import Fore, Back, Style, init

ver = 1.1
IS_TEST = True

tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]
NUM_HISTORY = 5
TIMEOUT = 60

init(autoreset=True)
CHAR_BOLD = '\033[1m'
CHAR_UNBOLD = '\033[0m'
CHAR_RESET = Back.RESET + Fore.RESET + Style.RESET_ALL + CHAR_UNBOLD

# STYLE_ACTIVE = CHAR_BOLD + Fore.RED + Style.BRIGHT
# STYLE_INACTIVE = CHAR_BOLD + Fore.YELLOW + Style.BRIGHT
STYLE_ACTIVE = Back.RED  + Fore.BLACK
STYLE_INACTIVE = Back.YELLOW + Fore.BLACK
STYLE_RESET = Back.RESET + Fore.RESET + Style.RESET_ALL + CHAR_UNBOLD

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

history_tgs = {}
for tg in tgs:
    history_tgs[tg] = []

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


def print_history(history_tgs):
    now = time.time()

    os.system('cls')

    if IS_TEST:
        print('***** TEST VERSION *****')

    for tg in tgs:
        text_tg = text_tg = '%s %-5d %s' % (STYLE_RESET, tg, STYLE_RESET)
        text_active = ''
        text_inactive = ''

        history_tg = history_tgs[tg]
        try:
            if history_tg[0]['Stop'] == 0:
                elapsed = now-history_tg[0]['Start']
                text_active = '%s, %s (%ds)' % (history_tg[0]['SourceCall'], history_tg[0]['SourceName'], elapsed) + ' '
                text_active = text_active.ljust(30, '-')
                callsigns = [d['SourceCall'] for d in history_tg[1:]]
                if len(callsigns) > 0:
                    text_inactive = ', '.join(callsigns)
                text_tg = '%s %-5d %s' % (STYLE_ACTIVE, tg, STYLE_RESET)
            else:
                text_inactive = ''
                for d in history_tg:
                    if now - d['Stop'] < TIMEOUT:
                        text_inactive = text_inactive + ('%s (%ds)' % (d['SourceCall'], now - d['Stop'])) + ', '
                text_inactive = text_inactive

                if len(text_inactive) > 0:
                    text_active = ''.ljust(30, '-')
                    text_tg = '%s %-5d %s' % (STYLE_INACTIVE, tg, STYLE_RESET)
        except Exception as e:
            a = 1

        print('%s | %s | %s' % (text_tg, text_active.ljust(30), text_inactive))

    print(Back.RESET + Fore.RESET + Style.RESET_ALL + CHAR_UNBOLD)
    print('Developed by Chanyeol Yoo (VK2CYO) v%.1f' % ver)
    print('https://github.com/chanyeolyoo/BMRMonitor')

    if is_update_available:
        print(Back.GREEN + Fore.BLACK + 'Update available: ' + resp_release['html_url'] + Style.RESET_ALL)
    else:
        print('Up-to-date')


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
            
        if time.time() - last_print >= 1:
            print_history(history_tgs)
            last_print = time.time()


loop = asyncio.get_event_loop()
queue = asyncio.Queue()
fetch = async_fetch(queue)
process = async_process(queue)
loop.run_until_complete(asyncio.gather(fetch,process))
loop.close()
