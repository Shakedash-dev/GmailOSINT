# GmailOSINT
Use Google services to gather details on an owner of a google account.<br>
Created for research purposes only. Don't use it on someone other than yourself.

# What it does?
Recieve phone number or gmail address.<br>
Returns:
  1. GAIA ID
  2. Full Name
  3. Addresses the account posted reviews on.
  4. Times the reviews taken.

## Warning!
It can sometimes pop a 2FA screen on the victim's phone, dependent on user's configuration.<br>
So <b> Do not use it on other people. Only yourself.</b>
  
# Installation
```
git clone https://github.com/Shakedash-dev/GmailOSINT.git & cd GmailOSINT
pip install requirements.txt
```
Can also be compiled using pyinstaller.

# Usage
```
python3 GmailOSINT.py john.doe@gmail.com
python3 GmailOSINT.py +12345678901
```
Can use `--sleep 20` or higher if the connection is slow.

# Example
![GmailOSINT POC](https://github.com/Shakedash-dev/GmailOSINT/blob/main/Example.png)


# Tested on
Windows 11, Python3.10.0
