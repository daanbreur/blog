---
date: "2021-04-24T00:00:00Z"
points: 300
redirect_from: /writeups/2021/CyberApocolypse2021/Authenticator.html
solves: 988
tags: [reversing,encryption]
title: '[Writeup] CyberApocolypse 2021 | Authenticator'
---

Solves: {{ page.solves }} \| Points: {{ page.points }}

We find a zip file with one file inside of it. When using ``file ./authenticator`` we can see its a ELF binary

```bash
file ./authenticator
```
```log
authenticator: ELF 64-bit LSB shared object, x86-64, 
version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, 
for GNU/Linux 3.2.0, BuildID[sha1]=66286657ca5a06147189b419238b2971b11c72db, not stripped
```

Lets open it in ghidra and use the decompiler

![](/assets/CTFs/CyberApocolypse2021/Authenticator/ghidra.png){: .modal}

Now that we have the file open in ghidra lets search for the *main* function and open it in the decompiler.

![](/assets/CTFs/CyberApocolypse2021/Authenticator/ghidra_decompiled_main.png){: .modal}

we see it will ask for a passcode thats our goal lets go the the function *checkpin*, that is being called with our input.

![](/assets/CTFs/CyberApocolypse2021/Authenticator/ghirda_decompiled_checkpin.png){: .modal}

Hmm lets make it more readable by rename variables.
It looks like it will loop over the length of the string and check if `"}a:Vh|}a:g}8j=}89gV<p<}:dV8<Vg9}V<9V<:j|{:"[index] ^ 9U` is equal to the character on the input, if not it will break and return 1.
return 1 in the main function is incorrect pincode, lets make a loop to decode that string

![](/assets/CTFs/CyberApocolypse2021/Authenticator/ghidra_decompiled_checkpin_annotated.png){: .modal}

I am going to use cpp because i only have to change a few lines from the checkpin function to make it work.

```cpp
#include <iostream>

using namespace std;
int main()
{
  int index;
  index = 0;
  while( true ) {
    if (index > 42) break;
    cout << static_cast<char>(("}a:Vh|}a:g}8j=}89gV<p<}:dV8<Vg9}V<9V<:j|{:"[index] ^ 9U));
    index = index + 1;
  }
  return 0;
}
```
^ A download for this script can be found [here](/assets/CTFs/CyberApocolypse2021/Authenticator/solver.cpp){: .modal}

This code will go over every character in that encoded string and doing an XOR with 9U. then it will cast that to an char and printing it to the console.

lets run the code and we get our flag, fill in in between CHTB{} and you get **CHTB{th3_auth3nt1c4t10n_5y5t3m_15_n0t_50_53cur3}**


Thanks for reading my writeup :)
