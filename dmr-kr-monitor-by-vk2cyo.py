
import asyncio
import websockets
import os
import datetime, time
import sys
import requests
from colorama import Fore, Back, Style

ver = 1.0

tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]

try:
    text_release = requests.get('https://api.github.com/repos/chanyeolyoo/BMRMonitor/releases/latest').text
    text_release = text_release.replace('false', 'False')
    text_release = text_release.replace('true', 'True')
    text_release = text_release.replace('null', 'None')
    resp_release = eval(text_release)
    tag_release = float(resp_release['tag_name'])

    if tag_release > ver:
        is_update_available = True
    else:
        is_update_available = False
except:
    is_update_available = False

history = []
for idx in range(len(tgs)):
    history.append({'tg':tgs[idx], 'data':{}})

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

def print_history(history):

    now = time.time()

    os.system('cls')

    for item in history:
        data = item['data']

        dstID = item['tg']
        try:
            if now-data['Start'] > 180:
                data = {}

            callsign = data['SourceCall']
            callname = data['SourceName']
            if data['Stop'] == 0:
                color = '\033[1m' + Fore.RED + Style.BRIGHT
                elapsed = now-data['Start']
                text = '%s, %s (Active for %ds)' % (callsign, callname, elapsed)
            else:
                color = '\033[1m' + Fore.YELLOW + Style.BRIGHT
                elapsed = now-data['Stop']
                text = '%s, %s (%ds ago)' % (callsign, callname, elapsed)
        except Exception as e:
            color = '\033[0m' + Back.RESET + Fore.RESET + Style.RESET_ALL
            text = ''

        text = "%-5d | %s" % (dstID, text)
        print('%s%-50s' % (color, text))
    print(Back.RESET + Fore.RESET + Style.RESET_ALL + '\033[0m')
    print('Developed by Chanyeol Yoo (VK2CYO) ver. %.1f' % ver)
    print('https://github.com/chanyeolyoo/BMRMonitor')

    if is_update_available:
        print()
        print(Back.GREEN + Fore.BLACK + 'Update available: ' + resp_release['html_url'] + Style.RESET_ALL)


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
            idx = tgs.index(dstID)
            history[idx]['data'] = data
            
        if time.time() - last_print >= 1:
            print_history(history)
            last_print = time.time()


loop = asyncio.get_event_loop()
queue = asyncio.Queue()
fetch = async_fetch(queue)
process = async_process(queue)
loop.run_until_complete(asyncio.gather(fetch,process))
loop.close()
