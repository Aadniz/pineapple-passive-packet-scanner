# Pineapple Passive Packet Scanner
A python script for the HAK5 Pineapple (Also works on Debian based systems like kali). Listen to packets, and trying to get hashes without deauthentication.
This script is meant to be ran for days, weeks or months

## Installation
Download the python script and install it by running it with `python passive.py`
Transfer the file via SFTP (for example)

## How it works

1. It scans for nearby WiFi networks (for 300 seconds)
2. Check the blacklist and other interfaces to avoid conflicts
3. If all networks are blacklisted, or other network interfaces are using up all the available networks, it will scan for longer
4. It will choose a network, and start capturing packets
5. Each 30 minutes, it will check if a hash is captured, otherwise it will clear the .cap file (to avoid HUGE files) and try again
6. If a hash is captured, it will add it to `/root/passive/captures/` and add the BSSID to the `blacklist.txt`
7. It will loop and find another WiFi

## Getting started
You can run it with `passive wlan0mon`
It supports multiple network interfaces at the same time, but you cannot run them in the same terminal

## Known issues
- The script will max out the CPU. This is because aircrack-ng is running *In the background*. There is a workaround for this using tmux (https://unix.stackexchange.com/a/359903/305898), but hasn't been able to install it. If anyone knows a fix for this, I would be happy to try them out

## NOTES
for blacklisting networks, put the BSSID or network name inside `/root/passive/blacklist.txt`
The file might look something like this:

    ## BLACKLIST LIST
    ##   The script will blacklist WIFI networks if a captured hash is found
    ##   You might also want to add your own
    ##   Add either BSSID example: "D4:02:0E:D2:22:3C" or ESSID example: "YourWifiName" (without quotes)\n
    78:D1:6E:0E:EE:24
    D4:02:0E:D2:22:3C
    YourWifiName
    22:94:71:6F:34:A7
    Another_wifi_name
