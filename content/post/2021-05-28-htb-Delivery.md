---
date: "2021-05-28T00:00:00Z"
redirect_from: /writeups/2021/HTB/Delivery.html
tags: [hackthebox,linux,web,passwordreuse,misconfiguration]
title: '[Writeup] HackTheBox | Delivery'
---

![](/assets/CTFs/HTB/Delivery/infopanel.png)

## Ports
```
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
8065/tcp open  unknown
```

## Reconnaissance
On port 8065 there is a Mattermost Server, its a sort of slack but selfhosted.

> Mattermost is an open-source, self-hostable online chat service with file sharing, search, and integrations. It is designed as an internal chat for organisations and companies, and mostly markets itself as an open-source alternative to Slack and Microsoft Teams.
>
> https://en.wikipedia.org/wiki/Mattermost

In the next image, we can see that an email is needed for mattermost.
![](/assets/CTFs/HTB/Delivery/mattermost-setup.png)

We cant use our own email but we need an `@delivery.htb`mail address.
How can we get an `@delivery.htb`mail address, lets check out what's on port 80 maybe we find something useful there.



On port 80 there is a a vhost for `helpdesk.delivery.htb` which has helpdesk software based on [OSTicket](https://osticket.com/). 

![](/assets/CTFs/HTB/Delivery/helpdesk-main.png)



![](/assets/CTFs/HTB/Delivery/helpdesk-create.png)

When we try to make a ticket we can see it asks for some information, lets enter a random email address in there and check if it accepts it. Make sure to remember what you entered.

![](/assets/CTFs/HTB/Delivery/helpdesk-ticketcreated.png)

It worked, on the page we now see a ticket id and an email. Awesome we get an `@delivery.htb` mail address, also what gets send to it will be displayed in the ticket.

![](/assets/CTFs/HTB/Delivery/helpdesk-ticketwithoutconfirmationmail.png)

Now make an account using the email address you got when making a ticket on mattermost.

![](/assets/CTFs/HTB/Delivery/helpdesk-ticketwithconfirmationmail.png)

After this refresh the helpdesk page for the ticket and you should see something like this, a confirmation URL for the account. After opening the URL (make sure to use the full one), you will be redirected to the login page. 

Login using the password you chose.
We are in it asked for the teams we want to join, lets click on *Internal*.And we are in and can read the chat.

![](/assets/CTFs/HTB/Delivery/mattermost-mainchat.png)



## Gaining Shell

At the top of the chat we see a message that says 

```markdown
@developers Please update theme to the OSTicket before we go live. Credentials to the server are maildeliverer:Youve_G0t_Mail! 
```

It gives us credentials for SSH, `Username: maildeliverer` and `Password: Youve_G0t_Mail!`.

After logging in, we can get the flag!
```bash
ls
# lse.sh  mattermost.txt  user.txt
cat user.txt
# REDACTED
```



## Enumeration

In the home directory there is a `.mysql_history` file, this tells us there is a MySQL server running. The MySQL server may also contain password hashes.
Now lets see if we can find the credentials for it. Maybe inside the mattermost configuration file, it can be found in `/opt/mattermost/config/config.json`

```json
"SqlSettings": {
    "DriverName": "mysql",
    "DataSource": "mmuser:Crack_The_MM_Admin_PW@tcp(127.0.0.1:3306)/mattermost?charset=utf8mb4,utf8\u0026readTimeout=30s\u0026writeTimeout=30s"
}
```

Yup it is in the configuration file, `Username: mmuser` and `Password: Crack_The_MM_Admin_PW`.

## Privilege Escalation

Lets connect to MySQL and see what we can find.

```bash
mysql -u mmuser -p -D mattermost
# Enter password: Crack_The_MM_Admin_PW
# MariaDB [mattermost]> 
```

So now that we are in MySQL, lets check what tables we have.

![](/assets/CTFs/HTB/Delivery/mysql-tables.png)

The table *Users* looks interesting, this may contain the passwords.

![](/assets/CTFs/HTB/Delivery/mysql-tables-user.png)

Lets run the following query to see what's in the table 
```sql
SELECT * FROM Users;
```

![](/assets/CTFs/HTB/Delivery/mysql-usertable.png)
Looks like it has a username and password field. Lets select those, where the username is *ROOT*
```sql
SELECT username,password FROM Users WHERE username='root';
```

![](/assets/CTFs/HTB/Delivery/mysql-rootpassword.png)

And we find the password hash for the root user. 
`username: root` and `password: $2a$10$VM6EeymRxJ29r8Wjkr8Dtev0O.1STWb4.4ScG.anuu7v0EFJwgjjO`

Lets start cracking that hash. We can find in the chat that the password is a variant of *PleaseSubscribe!*.

> Also please create a program to help us stop re-using the same passwords everywhere.... Especially those that are a variant of "PleaseSubscribe!"
> PleaseSubscribe! may not be in RockYou but if any hacker manages to get our hashes, they can use hashcat rules to easily crack all variations of common words or phrases.

Put the hash into a file `root.hash` and put `PleaseSubscribe!` into a file `root.dict`.

And use the following command.

```bash
sudo hashcat -w 1 -a 0 -m 3200 root.hash root.dict -r /usr/share/hashcat/rules/best64.rule
```
What does this command do?

- It sets the hash type to 3200, this is bcrypt.
- It sets the attack mode to 0, this is straight and will only use the wordlist and apply the rule file.
- It sets the workload profile to 1, this is the lowest one and perfect for my VM.
- It uses hash from the `root.hash` file.
- It uses the password from the `root.dict` file.
- It uses the `/usr/share/hashcat/rules/best64.rule` file for the password rules.

After a few minutes this will return with a password and it is `PleaseSubscribe!21`.

Lets switch to the root user.

```bash
su
# password:
cat /root/root.txt
# REDACTED
```
