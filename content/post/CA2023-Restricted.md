---
title: "CyberApocalypse 2023 | Restricted"
date: "2023-03-24T00:00:00Z"
tags: [misc]
categories: [CTF]
points: 300
---

Restricted was a challenge in the misc category. It's description says the following:

> You 're still trying to collect information for your research on the alien relic. Scientists contained the memories of ancient egyptian mummies into small chips, where they could store and replay them at will. Many of these mummies were part of the battle against the aliens and you suspect their memories may reveal hints to the location of the relic and the underground vessels. You managed to get your hands on one of these chips but after you connected to it, any attempt to access its internal data proved futile. The software containing all these memories seems to be running on a restricted environment which limits your access. Can you find a way to escape the restricted environment ?

There is a file download, lets download the files and open them up.
One of the files is a **Dockerfile** with the following content

```Docker
FROM debian:latest

RUN apt update -y && apt upgrade -y && apt install openssh-server procps -y

RUN adduser --disabled-password restricted
RUN usermod --shell /bin/rbash restricted
RUN sed -i -re 's/^restricted:[^:]+:/restricted::/' /etc/passwd /etc/shadow

RUN mkdir /home/restricted/.bin
RUN chown -R restricted:restricted /home/restricted

RUN ln -s /usr/bin/top /home/restricted/.bin
RUN ln -s /usr/bin/uptime /home/restricted/.bin
RUN ln -s /usr/bin/ssh /home/restricted/.bin

COPY src/sshd_config /etc/ssh/sshd_config
COPY src/flag.txt /flag.txt
COPY src/bash_profile /home/restricted/.bash_profile

RUN chown root:root /home/restricted/.bash_profile
RUN chmod 755 /home/restricted/.bash_profile
RUN chmod 755 /flag.txt

RUN mv /flag.txt /flag_`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 5 | head -n 1`

RUN ssh-keygen -A
RUN mkdir -p /run/sshd

EXPOSE 1337

ENTRYPOINT ["/usr/sbin/sshd", "-D", "-o", "ListenAddress=0.0.0.0", "-p", "1337"]
```

Looks like it sets up some things in a debian container. A user `restricted` with as shell `/bin/rbash`, this is a shell that is restricted in a few ways for example you are not able to use `/` in commands. Hmm ok, so how do we cat the flag?
Well there is a way to bypass this behavior by running the command as a "startup" command in ssh.

The command we need to get the flag is `cat /flag*`, lets try running it.

```
ssh restricted@DOCKERIP -p DOCKERPORT cat /flag*
```

![](/assets/CTFs/CyberApocalypse2023/Restricted/exploit.png)

And that worked, we got the flag!

**HTB{r35tr1ct10n5_4r3_p0w3r1355}**
