*Version 2.1 is out! It's a completely re-work, recreation from scratch*

# Pineapple Passive Packet Scanner
Passive packet scanner is a cli script meant to capture WPA handshakes without utilizing deauthentication.
It uses the aircrack commands, put them as threads and looks at the output after the thread is killed.
The script will utilize the wifi monitor interfaces, and silently listen to the closest hotspot.
Multiple interfaces is recommended.
You can start the script and have it run for hours/days/months.
Should work *out in the fields* / *on the move*, or just sitting in one place.
Again, the script does not utilize deauthentication, and should go un-noticed by any admin

## Screenshots

![Starting the script](/screenshots/Screenshot_20210908_050629.png "Starting")
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
*if no arguments is passed*
1. It will ask you what network interface to use
2. Press enter to continue, q to abort, or specify a number (network interfaces containing `mon` will be used)
3. It scans for nearby WiFi networks on specified network interfaces (for 1 minute)
4. Checks the blacklist and other interfaces to avoid conflicts
5. It will choose a network, and start capturing packets
6. Each 3 minutes, it will check if a handshake is captured, otherwise it will clear the .cap files (to avoid HUGE files) and try again
7. If a handshake is captured, it will add it to `/root/passive/captures/` and add the BSSID to the `blacklist.txt`
8. If a handshake is **NOT** found on chosen hotspot for over 10 minutes, it will scan again and chose another hotspot
9. It will loop and find another WiFi

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
 --uninstall     Removes folders and files related to the script except itself

 [Examples]:
  $ python passive.py -A -s 60*2 -c 60*3 -t 60*10 --loop 4 --no-colors
  $ passive -A -t 60*60*2 --no-colors
  $ passive -A -o /tmp
  $ passive -a -o /root/Documents/captures/
  $ passive -i wlan0mon wlan1mon wlan2mon -c 60*60
 ```

### Run in background
On the pinapple spesifically, there is no `nohup`, and there is no `disown`.
In that case, this should work:

    $ python passive.py [OPTIONS] 1>/dev/null 2>&1
    
Check that the process is running:

    $ jobs -l
    
Exit shell:

    $ exit

### Blacklist networks
for blacklisting networks, put the BSSID or network name inside `/root/passive/blacklist.txt`
This file is automatically created the first time you run the script.
The file might look something like this:

    ## BLACKLIST LIST
    ##   The script will blacklist WIFI networks if a captured handshake is found
    ##   You might also want to add your own
    ##   Add either BSSID example: "D4:02:0E:D2:22:3C" or ESSID example: "YourWifiName" (without quotes)
    78:D1:6E:0E:EE:24
    D4:02:0E:D2:22:3C
    YourWifiName  # Your wifi (yes, hashtag works like you think it would. comments)
    22:94:71:6F:34:A7
    Another_wifi_name

## NOTES
If you want to use another folder as the base folder, you can change the variable `datafolder` on line 21. Right now it's set to `/root/passive`

## TODO
 * Options for startup
 * Information of other hotspots found
 * automate hc22000 convertion
