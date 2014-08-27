#!/usr/bin/env python 
#spectool_ros.py
# Copyright 2013 Stephen Okay for Roadknight Labs
# Released under the GNU GPL V2

"""
This is a first whack at a python wrapper for the spectools_raw C tool.
spectools is a C-based package for reading data off a Metageek WiSpy spectrum analyzer
"""

import rospy
import sys
import os 
import socket
import threading
import Queue
import subprocess
import array
import mmap

class wispy (object):
	
	def __init__(self):
	#Check to see if we have a Wi-Spy attached as part of object init
		self.results=0
		self.has_wispy=0
		cmdq = Queue.Queue()

		proc=subprocess.Popen(['/usr/local/bin/spectool_raw','-l'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		(out,err)=proc.communicate()
		if out.count("Wi-Spy") >0 :
			#Found a wi-spy	
		   self.has_wispy=1
		   freqrange_idx=out.index("MHz")
		   sampl_idx=(out.find("samples"))-2
		   self.highfreq=int(out[freqrange_idx+4:freqrange_idx+8])
		   self.lowfreq=int(out[freqrange_idx-4:freqrange_idx])
		   self.samples=int(out[sampl_idx-1:sampl_idx+1])
             
		else:
		   print "No Wi-Spy attached"
		   self.has_wispy=0
	
	def speccheck(self):
		 has_spectool=False
                 s=subprocess.Popen(['which','spectool_raw'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)	
		 (sp,out)=s.communicate()
		 if "spectool_raw" in sp:
		    toolpath=sp.rstrip();
		    print "launching %s" % toolpath
		    has_spectool=True
		 else: 
		      print "Could not find spectool_raw binary...maybe spectools isn't installed?"
		 
                 return has_spectool 
        #main worker thread to split up incoming spectrum data
	def procline(self,specline):
	   if specline.startswith("Wi-Spy") and specline.count(":") == 1:
              specline=specline[specline.index(":")+1:]
              specline_l=[int(v) for v in specvals.split()]
	      return specline_l
	
	def specsmush(self,rawdata,queue):
	  for specline in iter(rawdata.readline, b''):
             queue.put(line)
    out.close()

	

		 
w=wispy()
if w.has_wispy == 1:
   print "Found a Wi-Spy device, scanning %d-%d MHz over %d samples" % (w.lowfreq,w.highfreq,w.samples)

   wisproc = subprocess.Popen([toolpath], stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
   wispq = Queue()
   withread = Thread(target=specsmush, args=(wisproc.stdout, wispq))
   withread.daemon = True # thread dies with the program
   withread.start()

else:
   print "No Wi-Spy attached"
   print "Exiting"
   sys.exit(-1)

