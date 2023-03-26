---
title: "CyberApocalypse 2023 | Remote Computation"
date: "2023-03-24T00:00:00Z"
tags: [misc]
categories: [CTF]
points: 300
---

Remote Computation was a challenge in the misc category. It's description says the following:

> The alien species use remote machines for all their computation needs. Pandora managed to hack into one, but broke its functionality in the process. Incoming computation requests need to be calculated and answered rapidly, in order to not alarm the aliens and ultimately pivot to other parts of their network. Not all requests are valid though, and appropriate error messages need to be sent depending on the type of error. Can you buy us some time by correctly responding to the next 500 requests?

Spawning the docker container we get a port and ip, lets connect to them using **netcat (nc)**.
![](/assets/CTFs/CyberApocalypse2023/RemoteComputation/menu.png)

After connecting we see a menu, lets use option two to get some help and see our objective.
And we get the following instructions
![](/assets/CTFs/CyberApocalypse2023/RemoteComputation/instructions.png)

```text
Results
---
All results are rounded
to 2 digits after the point.
ex. 9.5752 -> 9.58

Error Codes
---
* Divide by 0:
This may be alien technology,
but dividing by zero is still an error!
Expected response: DIV0_ERR

* Syntax Error
Invalid expressions due syntax errors.
ex. 3 +* 4 = ?
Expected response: SYNTAX_ERR

* Memory Error
The remote machine is blazingly fast,
but its architecture cannot represent any result
outside the range -1337.00 <= RESULT <= 1337.00
Expected response: MEM_ERR
```

Ok so we have to solve some mathematical equation, round to two digits and return some error when required.
Lets try starting now and see what the output looks like.
![](/assets/CTFs/CyberApocalypse2023/RemoteComputation/equation.png)

Now that we know the format we can write some code to automagically solve this for us.

```python
#!/usr/bin/env python3

from pwn import *

io = remote("DOCKERIP",DOCKERPORT)

io.recv()
io.send(b'1\n')

i = 1

while i <= 500:

    io.recvuntil(b']: ',drop=True)
    equation = io.recvuntil(b' = ?',drop=True)

    answer = ""

    try:
        answer = round(eval(equation.decode("utf-8")),2)
        if not (-1337.00 <= answer <= 1337.00):
            answer = b'MEM_ERR\n'
        else:
            answer = (str(answer)+"\n").encode()
    except ZeroDivisionError:
        answer = b'DIV0_ERR\n'
    except SyntaxError:
        answer = b'SYNTAX_ERR\n'

    log.info(f"{i}: {equation.decode()} with answer {answer.decode()}")
    io.send(answer)
    i+=1

io.recvuntil(b'Good job! ')
flag = io.recv().decode()
log.success("\n\n")
log.success(f"FLAG: {flag}")
log.success(f"FLAG: {flag}")
log.success(f"FLAG: {flag}")
```

Now lets run this script.

![](/assets/CTFs/CyberApocalypse2023/RemoteComputation/solve.png)

```text
[+] Opening connection to 188.166.152.84 on port 32727: Done
[*] 1: 9 / 20 + 17 / 29 - 29 + 21 - 17 / 15 + 29 * 8 + 19 - 12 with answer 230.9
[*] 2: 13 * 19 / 26 - 18 + 25 - 23 / 7 + 7 / 23 with answer 13.52
[*] 3: 7 / 28 - 29 + 5 / 20 * 20 * 5 + 20 + 19 * 2 / 20 / 12 + 28 - 17 with answer 27.41
[*] 4: 29 - 2 + 5 - 25 * 13 + 18 / 14 + 21 - 4 - 22 * 13 * 8 * 20 * 29 * 7 with answer MEM_ERR
[*] 5: 20 * 7 / 30 * 19 / 18 * 2 - 30 + 25 - 11 / 26 * 24 - 20 - 18 + 3 with answer -40.3
[*] 6: 23 + 5 / 12 * 25 * 17 / 21 / 17 - 14 * 12 - 22 + 6 / 4 with answer -165.0
[*] 7: 16 + 23 * 29 + 2 * 19 / 10 * 3 / 29 / 11 / 7 / 14 / 24 with answer 683.0
[*] 8: 24 / 20 / 8 - 29 * 6 + 6 - 13 * 29 + 16 + 20 with answer -508.85
[*] 9: 30 - 12 / 29 - 23 - 18 * 3 + 16 - 18 with answer -49.41
[*] 10: 16 + 8 * 5 / 18 + 15 / 3 * 21 + 4 - 6 / 25 - 16 - 24 * 18 - 17 - 9 with answer -347.02
[*] 11: 8 / 18 / 12 - 20 + 13 * 10 + 4 / 12 * 9 * 16 + 21 / 21 - 18 - 2 with answer 139.04
[*] 12: 14 * 6 - 15 * 30 / 3 + 17 * 19 - 22 / 7 + 26 - 29 - 7 - 4 - 22 with answer 217.86
[*] 13: 4 + 12 - 21 / 2 - 30 + 18 - 10 - 30 + 21 - 2 + 11 * 19 * 27 * 28 / 6 with answer MEM_ERR
[*] 14: 10 - 7 + 22 / 3 - 18 * 9 - 25 + 21 * 21 - 17 - 3 + 2 * 12 / 25 * 17 with answer 260.65
[*] 15: 5 + 16 + 30 - 26 / 7 - 25 + 20 + 15 + 15 + 30 * 4 - 25 with answer 167.29
[*] 16: 30 * 15 + 23 * 4 - 29 / 28 with answer 540.96
[*] 17: 30 + 7 / 29 + 22 + 14 / 15 + 17 * 20 - 28 * 21 + 7 * 19 - 26 - 13 with answer -100.83
[*] 18: 7 - 5 - 21 / 8 * 6 + 6 with answer -7.75
[*] 19: 10 * 3 * 2 / 30 + 12 * 26 + 22 - 14 + 28 - 20 with answer 330.0
[*] 20: 20 / 8 * 26 / 27 * 8 + 14 / 15 + 8 * 28 / 19 / 11 + 8 + 26 with answer 55.26
[*] 21: 18 / 14 / 27 * 20 - 24 - 26 / 11 * 2 * 18 / 23 + 29 + 18 * 9 - 23 / 29 with answer 163.46
[*] 22: 21 / 28 + 16 * 20 * 9 + 16 * 20 + 20 * 27 + 22 + 19 - 11 - 27 + 24 + 8 with answer MEM_ERR
[*] 23: 21 + 29 * 9 / 16 * 7 - 27 / 13 * 10 - 5 / 14 * 29 * 21 with answer -103.08
[*] 24: 20 + 22 * 20 * 28 * 3 - 2 + 21 / 17 - 15 + 26 / 7 / 15 / 13 with answer MEM_ERR
[*] 25: 3 * 15 / 6 / 29 / 6 with answer 0.04
[*] 26: 23 / 15 * 28 / 29 * 24 + 30 + 22 - 6 + 27 - 13 / 11 / 29 - 25 with answer 83.49
[*] 27: 23 - 12 / 10 - 21 * 2 * 14 + 26 with answer -540.2
[*] 28: 13 - 23 * 23 + 17 + 16 * 3 * 2 * 13 * 6 + 12 / 25 + 27 / 21 / 28 - 25 with answer MEM_ERR
[*] 29: 16 * 11 / 24 - 15 - 16 + 17 with answer -6.67
[*] 30: 14 - 22 + 20 + 10 * 2 * 6 * 27 * 4 / 29 - 8 * 11 with answer 370.9
[*] 31: 2 * 8 + 10 + 17 + 4 * 23 with answer 135
...
...
...
[*] 474: 26 + 24 + 8 + 18 + 26 - 13 * 13 - 20 with answer -87
[*] 475: 7 * 5 * 18 / 16 - 21 + 27 * 11 - 26 + 9 / 2 with answer 293.88
[*] 476: 3 - 22 - 9 / 19 * 20 * 16 with answer -170.58
[*] 477: 25 * 25 * 22 - 25 / 27 + 11 - 11 with answer MEM_ERR
[*] 478: 3 + 26 / 5 * 5 / 27 / 8 - 8 * 5 * 19 + 14 * 8 / 9 with answer -744.44
[*] 479: 21 * 27 + 26 / 20 + 3 + 7 - 28 with answer 550.3
[*] 480: 6 + 26 - 16 / 11 / 8 / 24 * 23 - 2 / 18 / 9 + 24 - 18 - 8 + 11 with answer 40.81
[*] 481: 5 * 25 - 28 + 18 / 14 * 25 / 10 / 4 with answer 97.8
[*] 482: 5 - 15 * 2 / 30 + 4 - 16 * 24 - 17 + 6 + 24 * 21 - 2 / 28 with answer 116.93
[*] 483: 23 + 29 / 2 * 18 + 28 - 18 with answer 294.0
[*] 484: 19 + 16 - 4 + 16 / 7 - 14 * 21 + 8 with answer -252.71
[*] 485: 15 * 20 / 17 * 20 * 17 with answer MEM_ERR
[*] 486: 8 + 23 + 12 + 29 - 3 / 24 + 12 / 25 * 6 * 10 - 8 - 12 + 21 - 20 / 27 with answer 100.93
[*] 487: 4 - 22 - 27 + 19 + 25 * 23 - 12 - 15 + 4 - 16 with answer 510
[*] 488: 14 * 30 - 6 - 16 * 28 / 15 - 27 - 4 - 9 / 15 + 3 + 13 * 4 - 14 / 22 with answer 406.9
[*] 489: 3 + 24 / 0 * 19 * 12 / 20 - 28 + 30 with answer DIV0_ERR
[*] 490: 25 + 12 * 28 * 27 / 18 / 29 * 28 + 20 / 19 with answer 512.67
[*] 491: 23 +* 28 / 28 / 20 * 27 + 24 / 10 / 8 with answer SYNTAX_ERR
[*] 492: 6 - 23 / 11 - 10 - 10 + 17 + 6 with answer 6.91
[*] 493: 4 * 21 + 25 - 29 + 11 + 3 * 4 * 22 + 26 / 12 / 28 - 30 - 5 with answer 320.08
[*] 494: 22 + 11 * 17 * 9 * 6 - 6 - 21 + 13 with answer MEM_ERR
[*] 495: 30 * 30 + 2 - 14 - 23 / 20 / 28 - 2 - 25 - 17 * 28 / 7 + 19 + 19 - 20 with answer 810.96
[*] 496: 3 / 25 - 7 * 17 - 2 * 23 / 23 + 29 with answer -91.88
[*] 497: 3 - 13 / 19 - 13 * 12 / 21 * 25 + 10 / 29 with answer -183.05
[*] 498: 30 / 29 * 4 - 18 * 4 / 21 - 12 - 30 / 26 - 8 with answer -20.44
[*] 499: 26 * 19 - 9 + 3 / 4 with answer 485.75
[*] 500: 25 * 19 /* 14 - 23 / 21 * 29 - 25 - 26 + 9 - 12 + 4 - 2 * 20 * 4 * 24 with answer SYNTAX_ERR
[+]

[+] FLAG: HTB{d1v1d3_bY_Z3r0_3rr0r}
[+] FLAG: HTB{d1v1d3_bY_Z3r0_3rr0r}
[+] FLAG: HTB{d1v1d3_bY_Z3r0_3rr0r}
[*] Closed connection to 188.166.152.84 port 32727
```

It runs for a little while and then boom the flag!

**HTB{d1v1d3_bY_Z3r0_3rr0r}**
