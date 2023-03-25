---
title: "CyberApocalypse 2023 | Trapped Source"
date: "2023-03-24T00:00:00Z"
tags: [web]
categories: [CTF]
points: 300
---

Trapped Source was a challenge in the web category. It's description says the following:

> Intergalactic Ministry of Spies tested Pandora's movement and intelligence abilities. She found herself locked in a room with no apparent means of escape. Her task was to unlock the door and make her way out. Can you help her in opening the door?

Spawning the docker container and opening the website we see the following page.
![](/assets/CTFs/CyberApocalypse2023/TrappedSource/mainscreen.png)

Hmmm, what would the pincode be? Lets inspect the source-code.

```html
<!DOCTYPE html>
<html lang="en">
	<head>
		<meta charset="UTF-8" />
		<title></title>
		<link rel="stylesheet" href="/static/css/style.css" />
		<link rel="stylesheet" href="/static/css/bootstrap.min.css" />
	</head>

	<body>
		<script>
			window.CONFIG = window.CONFIG || {
				buildNumber: "v20190816",
				debug: false,
				modelName: "Valencia",
				correctPin: "8291",
			};
		</script>
		<div class="lockbox">
			<div class="lockStatus">LOCKED</div>
			<div class="lockMid">
				<span id="btn9" class="button" onclick="unlock(9)">9</span>
				<span id="btn8" class="button" onclick="unlock(8)">8</span>
				<span id="btn7" class="button" onclick="unlock(7)">7</span>
				<span id="btn6" class="button" onclick="unlock(6)">6</span>
				<span id="btn5" class="button" onclick="unlock(5)">5</span>
				<span id="btn4" class="button" onclick="unlock(4)">4</span>
				<span id="btn3" class="button" onclick="unlock(3)">3</span>
				<span id="btn2" class="button" onclick="unlock(2)">2</span>
				<span id="btn1" class="button" onclick="unlock(1)">1</span>
				<div class="clear" onclick="reset()">Clear</div>
				<div class="scoreCount" onclick="checkPin()">Enter</div>
			</div>
		</div>

		<!-- partial -->
		<script src="/static/js/jquery.js"></script>
		<script src="/static/js/script.js"></script>
	</body>
</html>
```

We see a very interesting `<script></script>` that configures some variables. One of which is `correctPin`, the code is set to `8291`.

```javascript
window.CONFIG = window.CONFIG || {
	buildNumber: "v20190816",
	debug: false,
	modelName: "Valencia",
	correctPin: "8291",
};
```

Lets try entering this pincode and see what happens.
![](/assets/CTFs/CyberApocalypse2023/TrappedSource/pincode_entered.png)

Hey that worked! We got the flag. As we can see the title was a tiny hint, Trapped Source and the pincode was "Trapped" in the source.

**HTB{V13w_50urc3_c4n_b3_u53ful!!!}**
