"""
Brandmeister DMR Monitor for Korean Talkgroups

Author: Chanyeol Yoo (VK2CYO)
Copyright: Chanyeol Yoo, Ph.D. (VK2CYO), 2020
License: MIT
Version: v1.11
Maintainer: Chanyeol Yoo (VK2CYO)
Email: vk2cyo@gmail.com
URL: https://github.com/chanyeolyoo/BMRMonitor

Copyright (c) 2020 Chanyeol Yoo, Ph.D. (VK2CYO)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import websockets
import os
import datetime, time
import sys
import requests
from colorama import Fore, Back, Style, init
import sqlite3

import flask
from flask import request, jsonify
import json

ver = 1.11
IS_TEST = False

tgs = [450, 45021, 45022, 45023, 45024, 45025, 45026, 45027, 45028, 45029]  # TALKGROUPS TO BE MONITORED
NUM_HISTORY = 5     # NUMBER OF HISTORY FOR EACH TALKGROUP
TIMEOUT = 180      # TIMEOUT FOR INACTIVE CALLS
NUM_PADD = 30       # NUMBER OF EMPTY SPACES IN ACTIVE CALL FIELD

#### PARAMETERS FOR PRINTING TO TERMINAL
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

# conn = sqlite3.connect('database.db', isolation_level=None)
conn = sqlite3.connect('database.db')
# conn.execute('''DROP TABLE entries;''')
# conn.execute('''DROP TABLE talkgroups;''')
conn.execute('''CREATE TABLE IF NOT EXISTS entries (SourceCall text, SourceName text, DestinationID NUMERIC, Start NUMERIC, Stop NUMERIC)''')
conn.execute('''CREATE TABLE IF NOT EXISTS talkgroups (id NUMERIC, name TEXT)''')


for tg in tgs:
    conn.execute('''INSERT INTO talkgroups VALUES (%d, '%s')''' % (tg, ''))
conn.commit()

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

def get_dict_from_query(conn, query_str):
    exec = conn.execute(query_str)

    fieldnames = [d[0] for d in exec.description]
    rows = exec.fetchall()
    results = []
    for row in rows:
        data = dict(zip(fieldnames, row)) 
        results.append(data)

    return results

"""
PRINT_HISTORY
    - Prints "history_tgs" in terminal
"""
def print_history():
    now = time.time()

    if sys.platform == 'linux':
        os.system('clear')
    else:
        os.system('cls')

    if IS_TEST:
        print('***** TEST VERSION *****')

    conn.execute('''DELETE FROM entries WHERE Stop>0 AND %d-Stop>%d;''' % (now, TIMEOUT))
    conn.commit()

    for tg in tgs:
        text_tg = text_tg = '%s %-5d %s' % (STYLE_RESET, tg, STYLE_RESET)
        text_active = ''
        text_inactive = ''

        active_all = get_dict_from_query(conn, '''SELECT * FROM entries WHERE DestinationID=%d AND Stop=0 ORDER BY Start DESC;''' % (tg))
        inactive_all = get_dict_from_query(conn, '''SELECT * FROM entries WHERE DestinationID=%d AND Stop>0 ORDER BY Stop DESC;''' % (tg))
            
        text_inactive = ''
        for inactive in inactive_all:
            text_inactive = text_inactive + ('%s (%ds), ' % (inactive['SourceCall'], now - inactive['Stop']))

        if len(active_all) > 0:
            text_tg = '%s %-5d %s' % (STYLE_ACTIVE, tg, STYLE_RESET)
            text_active = '%s, %s (%ds) ' % (active_all[0]['SourceCall'], active_all[0]['SourceName'], now - active_all[0]['Start'])
        
        
        if len(active_all) > 0:
            text_tg = '%s %-5d %s' % (STYLE_ACTIVE, tg, STYLE_RESET)
        elif len(inactive_all) > 0:
            text_tg = '%s %-5d %s' % (STYLE_INACTIVE, tg, STYLE_RESET)
            text_active = text_active.ljust(NUM_PADD, '-')

        print('%s | %s | %s' % (text_tg, text_active.ljust(NUM_PADD), text_inactive))

    print('Developed by Chanyeol Yoo (VK2CYO) v%.2f' % ver)
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

            except Exception as e:
                print('RESTART: ' + e.__str__())

"""
ASYNC_PROCESS
    - Waits for queue data
    - When there is string data in "queue", it calls "sort_data_by_time" function
"""
async def async_process(queue):
    while True:
        str = await queue.get()
        data = get_data_from_packet(str)

        if data==None:
            continue

        if data['DestinationID'] in tgs:
            dstID = data['DestinationID']

            prevs = get_dict_from_query(conn, '''SELECT * FROM entries WHERE sourceCall = '%s' AND destinationID = %d;''' % (data['SourceCall'], data['DestinationID']))
            if len(prevs) == 0:
                conn.execute('''INSERT INTO entries VALUES ('%s','%s',%d,%d,%d)''' % (data['SourceCall'], data['SourceName'], data['DestinationID'], data['Start'], data['Stop']))
            # elif (data['Stop'] > prevs[0]['Stop']) or (data['Stop']==0 and data['Start'] > prevs[0]['Start']):
            else:
                conn.execute('''UPDATE entries SET start = %d, stop = %d WHERE sourceCall = '%s' AND destinationID = %d;''' % (data['Start'], data['Stop'], data['SourceCall'], data['DestinationID']))
            
            
            # history_tgs[dstID] = sort_data_by_time(history_tgs[dstID] + [data])
            
"""
ASYNC_PRINT
    - Prints to terminal every one second
"""
async def async_print():
    while True:
        await asyncio.sleep(1.0)
        print_history()

"""
Starts main loop
"""
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    afetch = async_fetch(queue)
    aprocess = async_process(queue)
    aprint = async_print()

    

    loop.run_until_complete(asyncio.gather(afetch, aprocess, aprint))
    loop.close()
