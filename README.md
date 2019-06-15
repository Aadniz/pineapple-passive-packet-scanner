# pineapple-passive-packet-scanner
A python script for the HAK5 Pineapple. Listen to packets, and trying to get hashes without deauthentication.
This script is meant to be ran for days, weeks or months

## Installation
Download the python script, and put it inside /root/passive_hack
Transfer the file via SFTP (for example)

## NOTES
for blacklisting networks, put the BSSID inside blacklist.txt
The file might look something like this:

    78:D1:6E:0E:EE:24
    D4:02:0E:D2:22:3C
    22:94:71:6F:34:A7
