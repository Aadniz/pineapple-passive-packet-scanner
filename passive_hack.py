import os
import subprocess
import time
import signal
import glob, os, os.path
import sys

interface = ""
scan_interval = 40 # 5 minutes

if len(sys.argv) == 2:
	interface = sys.argv[1]
else:
	print ("No interface provided..")
	print ("Example: \"passive_hack.py wlan0mon\"")
	exit()

def scan(interface, scan_interval):
	#process[] = subprocess.Popen("airodump-ng "+interface+" -w /root/scripts/passive_hack/scans/scan-"+interface+" --write-interval 15 -o csv", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process = subprocess.Popen(
		"airodump-ng "+interface+" -w /root/passive_hack/scans/scan-"+interface+" --write-interval "+str(int(scan_interval//9))+" -o csv & sleep "+str(scan_interval)+" ; kill $!",
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)
	time.sleep(scan_interval + 15)

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




#c=0
#for interface in interfaces:
#	process[c].terminate()
#	c+=1


#process = subprocess.Popen(cmd, shell=True)
#time.sleep(5)
#os.kill(process.pid, signal.SIGINT)