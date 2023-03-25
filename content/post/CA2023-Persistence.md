---
title: "CyberApocalypse 2023 | Persistence"
date: "2023-03-24T00:00:00Z"
tags: [misc]
categories: [CTF]
points: 300
---

Persistance was a challenge in the misc category, the description reads as follows

> Thousands of years ago, sending a GET request to /flag would grant immense power and wisdom. Now it's broken and usually returns random data, but keep trying, and you might get lucky... Legends say it works once every 1000 tries.

And there is a docker to spawn, this docker might be a website and /flag will probably return the flag. But like the text says it only returns it once every 1000 tries.

Easy right? How would be solve this? I chose for the bruteforce way, I wrote a little python script that keep trying and when it gets data that contains a flag (HTB{.\*}) it stops and print out that response. Let's take a look at the code.

```python
#!/usr/bin/env python3

import requests

URL = 'http://<DOCKERIP>/flag'

while True:
  x = requests.get(URL)
  data = x.text
  if 'HTB' in data:
    print(f'[FLAG] Data: {data}')
    break
  else:
    print(f'[----] Data: {data}')
```

After running this script it outputs something like this.

```text
[----] Data: zGb;1;~8C"j+.)z/
[----] Data: i$35M9_"a3_0uAC,LQhx/lzUf)tQ
[----] Data: j_k)4N\X[+n&s"=5!
[----] Data: ;\)OQBf)(Ss!#uK'6G%Cj"L.1p7?U
[----] Data: z^J/A.th=._{(.?{2wqE*~Yuf9
[----] Data: 1x<_PZpv".&3!scOc{073iNo@K086
[----] Data: D01?+[)/c4y[9IUrlc@wnjn7FRMF&J
...
...
...
[----] Data: md|Q_-vD,eu6)nz<Q)f$
[----] Data: _0>x#_dIfN/gq"SMtM
[----] Data: 2nTG,<}*UXsM$e%.dx`R
[----] Data: ulK\Br9K\!XDL~tgj
[----] Data: (z}hsiVrE(v5iz2
[----] Data: 2&pL~saTG<6.**g$I9"L(rbRc
[----] Data: ps#^1ROlsw^P?tnqaSH\pe
[----] Data: ]G!,{!TPO<-jy:y\
[FLAG] Data: HTB{y0u_h4v3_p0w3rfuL_sCr1pt1ng_ab1lit13S!}
```

And as you can see it returns us the flag!
**HTB{y0u_h4v3_p0w3rfuL_sCr1pt1ng_ab1lit13S!}**
