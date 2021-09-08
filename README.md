*Version 2.1 is out! It's a completely re-work, recreation from scratch*

# Pineapple Passive Packet Scanner
A python script for the HAK5 Pineapple (Also works on Debian based systems like kali). Listen to packets, and trying to get hashes without deauthentication.
It calls aircrack commands, but automate the process
This script is meant to be ran for days, weeks or months

## Screenshots

![Starting the script](/screenshots/Screenshot_20210908_045026.png "Starting")
<!--![100% CPU issue if fixed. 3 network interfaces stable around 3% CPU](/screenshots/Screenshot_20210905_154359_censor.png "100% CPU issue")
![Finding a handshake](/screenshots/Screenshot_20210906_070527_censor.png "Finding a handshake")-->
<!--| Screenshots|
|------------|
| <img src="/screenshots/Screenshot_20210905_154911_censor.png" width=49%> <img src="/screenshots/Screenshot_20210906_070527_censor.png" width=49%> |
| <img src="/screenshots/Screenshot_20210905_154359_censor.png" width=100%> |-->

## Installation
Download the python script and install it by running it with `python passive.py`.
For the Pineapple, transfer the file via SFTP (for example)

## How it works

1. It scans for nearby WiFi networks (for 300 seconds)
2. Check the blacklist and other interfaces to avoid conflicts
3. It will choose a network, and start capturing packets
4. Each 20 minutes, it will check if a hash is captured, otherwise it will clear the .cap files (to avoid HUGE files) and try again
5. If a hash is captured, it will add it to `/root/passive/captures/` and add the BSSID to the `blacklist.txt`
6. It will loop and find another WiFi

## Getting started
You can run it with `passive`, or just continue using `python passive.py`
It supports multiple network interfaces at the same time!

### Arguments
Arguments supported right now are these:
```
Option          Meaning
 -h, --help      Displays this help menu
 -a              use all available wifi monitoring interfaces already set in monitor mode (Default: user input choice)
 -A              use all available wifi monitoring interfaces (Default: user input choice)
 -i              Specify network interfaces to use (Default: user input choice)
 -s              Specify seconds for scanning (Default: 60)
 -c              Specify seconds for capturing (Default: 60*3)
 -t              Specify seconds before giving up on capturing, and looks for another hotspot (Default: 60*10)
 -o              Specify output folder for success handshakes captured (Default: /root/passive/captures)
 -v, --version   Displays the version

 [Extra options]:
Option          Meaning
 --no-colors     Disable colors (Default: False)
 --loop          Specify seconds for main loop (value must be more than 0) (Default: 5)

 [Examples]:
  python passive.py -A -s 60*2 -c 60*3 -t 60*10 --loop 4 --no-colors
  passive -A -t 60*60*2 --no-colors
  passive -A -o /tmp
  passive -a -o /root/Documents/captures/
  passive -i wlan0mon wlan1mon wlan2mon -c 60*60
 ```

## Blacklist networks
for blacklisting networks, put the BSSID or network name inside `/root/passive/blacklist.txt`
This file is automatically created the first time you run the script.
The file might look something like this:

    ## BLACKLIST LIST
    ##   The script will blacklist WIFI networks if a captured hash is found
    ##   You might also want to add your own
    ##   Add either BSSID example: "D4:02:0E:D2:22:3C" or ESSID example: "YourWifiName" (without quotes)
    78:D1:6E:0E:EE:24
    D4:02:0E:D2:22:3C
    YourWifiName
    22:94:71:6F:34:A7
    Another_wifi_name

## NOTES
If you want to use another folder as the base folder, you can change the variable `datafolder` on line 21. Right now it's set to `/root/passive`

## TODO
 * Improve use of arguments
 * More arguments (uninstall, systemd, control the timers)
 * Information of other hotspots found
 * automate hc22000 convertion
