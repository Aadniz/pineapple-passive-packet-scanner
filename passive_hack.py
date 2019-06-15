import os
import subprocess
import time
import signal
import glob, os, os.path

interfaces = []

def getinterfaces():
	global interfaces
	interfaces = []
	mydir = "/root/scripts/passive_hack/scans/"
	filelist = [ f for f in os.listdir(mydir) if f.endswith(".csv") ]
	for f in filelist:
		os.remove(os.path.join(mydir, f))

	for interface in os.listdir('/sys/class/net/'):
		if "wlan" in interface and "mon" in interface:
			interfaces.append(interface)

def scan(interface, scan_interval):
	interfaces = []
	#process[] = subprocess.Popen("airodump-ng "+interface+" -w /root/scripts/passive_hack/scans/scan-"+interface+" --write-interval 15 -o csv", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process = subprocess.Popen(
		"airodump-ng "+interface+" -w /root/scripts/passive_hack/scans/scan-"+interface+" --write-interval "+str(int(scan_interval//9))+" -o csv & sleep "+str(scan_interval)+" ; kill $!",
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)

def findnexttarget():
	print ("agggggggggggg")

def capture(interface):
	process = subprocess.Popen(
		"airodump-ng "+interface+" -w /root/scripts/passive_hack/scans/scan-"+interface+" --write-interval "+str(int(scan_interval//9))+" -o csv & sleep "+str(scan_interval)+" ; kill $!",
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE
	)

getinterfaces()
for interface in interfaces:
	scan(interface, 420)

time.sleep(420+15)


#c=0
#for interface in interfaces:
#	process[c].terminate()
#	c+=1


#process = subprocess.Popen(cmd, shell=True)
#time.sleep(5)
#os.kill(process.pid, signal.SIGINT)