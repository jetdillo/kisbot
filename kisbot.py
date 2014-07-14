#!/usr/bin/env python 
#kisbot.py
# Copyright 2013 Stephen Okay for Roadknight Labs
# Released under the GNU GPL V2

"""
ROS-related modules for publishing RSSI data from spectools,wireless-tools, etc. 
"""

import rospy
import threading
import Queue
from std_msgs.msg import String,Int16MultiArray,MultiArrayDimension
import sys
import os 
import socket
import subprocess
import array
import mmap

class wispy (object):

        def __init__(self):
        #Check to see if we have a Wi-Spy attached as part of object init
                self.has_wispy=False

		p=subprocess.Popen(['lsusb'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(out,err)=p.communicate()
		print out
		if "MetaGeek" in out:
			self.has_wispy=True
                       	 #Found a wi-spy, now get some stats
                	proc=subprocess.Popen(['/usr/local/bin/spectool_raw','-l'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                	(out,err)=proc.communicate()

                	if out.count("Wi-Spy") >0 :
                   		freqrange_idx=out.index("MHz")
                   		sampl_idx=(out.find("samples"))-2
                   		self.highfreq=int(out[freqrange_idx+4:freqrange_idx+8])
                   		self.lowfreq=int(out[freqrange_idx-4:freqrange_idx])
                   		self.samples=int(out[sampl_idx-1:sampl_idx+1])

                	else:
                   		print "No Wi-Spy attached"
                   		self.has_wispy=0

	def detect(self): 
		hasdevice=False
		p=subprocess.Popen(['lsusb'])
		(out,err)=p.communicate()
		if "MetaGeek" in out:
			hasdevice=True
		return hasdevice		

	def liner(self,specline,range):
		channels=[0,0,0]
       		if "Wi-Spy" in specline and ":" in specline:
			specdata=specline[specline.index(":")+2:].split()
		   	if range == 1:
		      		channels=[int(specdata[12]),int(specdata[37]),int(specdata[62])]
		   	else:
		      		channels=specdata
		return channels

	#Reads data off the Wi-Spy Popen handle and writes it into the queue
	def wisper(self,out,wisperq):
		for wisperline in iter(out.readline,b''):
			wisperq.put(wisperline)
		out.close()
	

	def initscan(self):
	
		specproc=subprocess.Popen(['/usr/local/bin/spectool_raw'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		wisperq=Queue.Queue()

		#Kick off the spectool reader thread
		wisper_t=threading.Thread(target=self.wisper,args=(specproc.stdout,wisperq))
		wisper_t.daemon=True
		wisper_t.start()
		
		#Wait until we've got some messages in the queue
		#This will load up pretty quick 	
		if wisperq.qsize >100:
			print wisperq.qsize
			self.publisher(wisperq)

	def publisher(self,queue):
		numchans=3
		rfdata=Int16MultiArray()	
		rfdata.layout.dim = [MultiArrayDimension('rfdata',numchans,1)]
		if numchans == 3:
			chanmode=1
		else:
			chanmode=14
		pub = rospy.Publisher('rfdata', Int16MultiArray)
		rospy.init_node('wisper')
			
		while not rospy.is_shutdown():
				wisperline=queue.get()
				chandata=self.liner(wisperline,chanmode)
				rfdata.data=chandata
				pub.publish(rfdata)
				rospy.loginfo(rfdata)

#get RSSI data from iw/wireless-tools commands
#Needs wireless-tools package and an amenable (e.g., Atheros) chipset

class iwtool(object):

	def __init__(self):
		self.has_iw=False
		self.iw_iface=''
		self.iw_str=''
		self.iwproc=subprocess.Popen(['iwconfig'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(out,err)=self.iwproc.communicate()
			
		if out.count("ESSID")==1:
			self.has_iw=True
			for l in out.split("\n"):
			   if "IEEE" in l:
				self.iw_iface=l[0:4]
				self.iw_str=out[out.find(self.iw_iface):]
		else:
			self.has_iw=False

class horst(object):
	
	def __init__(self):
	   
