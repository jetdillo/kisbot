import subprocess
import re
import pdb
import time
import timeit
from collections import deque,Counter
import numpy
import rospy
import sys
from kisbot.msg import KisbotIWScanData
from kisbot.cfg import KisbotConfig as ConfigType

class IWScan():

   def __init__(self,iface):
     
      self.dev=iface 
      init_message = rospy.get_param('~hwaddr', '13:37:ca:fe:d0:0d')
      rate = float(rospy.get_param('~rate', '1.0'))
      rospy.loginfo('rate = %d', rate)
      pub=rospy.Publisher('iwscan',KisbotIWScanData)

      msg=KisbotIWScanData() 
      msg.qual=0
      msg.rssi=-100
      msg.message=init_message     

      while not rospy.is_shutdown():
         scan(self.dev,'short')
         for k in apd.keys():
         if not k in scan_hist_d.keys():
            print "Added %s " % k
            scan_hist_d[k]=apd[k]
         else:
             if len(scan_hist_d[k]) < 10:
                scan_hist_d[k].extend(apd[k])
             else: 
                zqual=[scan_hist_d[k][s] for s in xrange(0,10,2)]
                zrssi=[scan_hist_d[k][s] for s in xrange(1,10,2)]
                #qual=rssi_freq(zqual,k)
                #rssi=rssi_freq(zrssi,k)
                qual=rssi_avg(zqual,k)
                rssi=rssi_avg(zrssi,k)
                #qual=rssi_kal(zqual,10,zqual[5])
                #rssi=rssi_kal(zrssi,10,zrssi[5])
                print "MAC:%s quality:%s rssi:%s RAW: %s" % (k,qual,rssi,scan_hist_
   d[k])        
                msg.hwaddr=k
                msg.qual=qual
                msg.signal=rssi
                pub.publish(msg)
                scan_hist_d[k]=[]
                if rate:
                   rospy.sleep(1/rate)
                else:
                   rospy.sleep(1.0)

    def scan(self,iface,mode='long'):
      scan_d={}   
      station_d={}
      scan_l=[]
      mac=""
      incell=False
      scan_ts=0
      proc=subprocess.Popen(['/sbin/iwlist',iface,'scanning'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
      (out,err)=proc.communicate()
      celldata=deque(out.split('Cell'))
      scan_ts=time.time()   
      celldata.popleft()
      if mode == 'long':
         for c in celldata:
            cellines=c.split("\n")
            mac=cellines[0].split()[3]
            scan_l.append(scan_ts)
            scan_l.append(cellines[1].split(':')[1])
            qualstr=cellines[3].split()
            scan_l.append(qualstr[0].split('/')[0])
            scan_l.append(qualstr[2].split('=')[1])
            scan_l.append(cellines[5].split(':')[1].strip('"'))
            beacontime=cellines[11].split()[3]
            scan_l.append(beacontime[0:(beacontime.index("ms"))])
            scan_d[scan_ts]=scan_l 
            scan_l=[]
      else: 
         for c in celldata:
            cellines=c.split("\n")
            mac=cellines[0].split()[3]
            qualstr=cellines[3].split()
            #scan_l.append(scan_ts)
            scan_l.append(float(qualstr[0].split('=')[1].split('/')[0]))
            scan_l.append(float(qualstr[2].split('=')[1]))
            scan_d[mac]=scan_l 
            scan_l=[]
            
      return scan_d
            
   def rssi_kal(self,z,zsize,xhat_guess):
   # intial parameters
      n_iter = 10
      sz = (n_iter,) # size of array
      x = -46.00 # truth value (typo in example at top of p. 13 calls this z)
      #z = numpy.random.normal(x,0.1,size=sz) # observations (normal about x, sigma=0.1)
   
      Q = 1e-5 # process variance
   
   # allocate space for arrays
      xhat=numpy.zeros(sz)      # a posteri estimate of x
      P=numpy.zeros(sz)         # a posteri error estimate
      xhatminus=numpy.zeros(sz) # a priori estimate of x
      Pminus=numpy.zeros(sz)    # a priori error estimate
      K=numpy.zeros(sz)         # gain or blending factor
   
      R = 0.1**2 # estimate of measurement variance, change to see effect
   
   # intial guesses
      xhat[0] = xhat_guess
      P[0] = 0.5
   
      for k in range(1,n_iter):
       # time update
          xhatminus[k] = xhat[k-1]
          Pminus[k] = P[k-1]+Q
   
       # measurement update
          K[k] = Pminus[k]/( Pminus[k]+R )
          xhat[k] = xhatminus[k]+K[k]*(z[k]-xhatminus[k])
          P[k] = (1-K[k])*Pminus[k]
          #print "xhat=%f xhatminus=%f" % (xhat[k],xhatminus[k])
      #RSSI comes in as an int so we reduce back to that 
      xhatint=[int(x) for x in xhat]
      return xhatint
  
   def rssi_freq(self,rssi_vals,mac):
   #rssi based on frequency count
      rssi_counts=Counter(rssi_vals) 
      print "%s %s" % (mac,rssi_counts)
      return rssi_counts.keys()[0]
   
   def rssi_avg(rssi_vals,mac):
      rssi_s=deque(sorted(rssi_vals))
      rssi_s.popleft()
      rssi_s.pop()
      print "%s %s" % (mac,rssi_vals)
      return sum(rssi_s)/len(rssi_s)
   
if __name__ == '__main__':
   scan_hist_d={}
   samples=5
 
   rospy.init_node('kisbot')
   try: 
      iws=IWScan()
   except rospy.ROSInterruptException: pass
