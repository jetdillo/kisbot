#!/usr/bin/env python
'''a really simple implementor for kisbot.
   Run roscore in another shell/process and look for the /rfdata topic'''
import kisbot
w=kisbot.wispy()
if w.has_wispy == True:
	w.initscan()
else:
	print "No Wi-Spy detected! Please attach one to an available USB port"
	sys.exit(-1)
