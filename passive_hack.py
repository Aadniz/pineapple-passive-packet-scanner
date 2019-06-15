#!/usr/bin/env python
import os
import subprocess
import time
import signal
import glob, os, os.path
import sys
import random
import shutil

interface = ""
scan_interval = 15 # 5 minutes

def firsttime():
	os.makedirs("/root/passive_hack/")
	os.makedirs("/root/passive_hack/scans/")
	os.makedirs("/root/passive_hack/captures/")
	open("/root/passive_hack/blacklist.txt", 'a').close()
	shutil.copy(__file__, '/root/passive_hack/passive_hack.py')
	shutil.copy(__file__, '/usr/bin/passive')
	print ("successfully installed")
	print ("run with this command:")
	print ("  passive wlan0mon")
	exit()

if os.path.isdir("/root/passive_hack/") == False:
	firsttime()

if len(sys.argv) == 2:
	interface = sys.argv[1]
else:
	print ("No interface provided..")
	print ("Example: \"passive_hack.py wlan0mon\"")
	exit()


def scan(interface, scan_interval):
	process = subprocess.Popen(
		"airodump-ng "+interface+" -w /root/passive_hack/scans/scan-"+str(random.randint(1, 100))+interface+" -o csv & sleep "+str(scan_interval)+" ; kill $!",
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	out, err = process.communicate()

def findnexttarget():
	print ("agggggggggggg")

def capture(interface):
	process = subprocess.Popen(
		"airodump-ng "+interface+" -w /root/passive_hack/scans/scan-"+interface+" --write-interval "+str(int(scan_interval//9))+" -o csv & sleep "+str(scan_interval)+" ; kill $!",
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)

scan(interface, scan_interval)
#test(interface, scan_interval)




#c=0
#for interface in interfaces:
#	process[c].terminate()
#	c+=1


#process = subprocess.Popen(cmd, shell=True)
#time.sleep(5)
#os.kill(process.pid, signal.SIGINT)