import subprocess
import re


def scan(iface):
   scan_d={}   
   scan_l=[]
   mac=""
   incell=False

   proc=subprocess.Popen(['/sbin/iwlist',iface,'scanning'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   (out,err)=proc.communicate()
   scanlines=out.split('\n')
   
   for s in scanlines:
      if "Cell" in s:
         mac=s.split()[4]
         incell=True
      if "Channel" in s and incell==True:
         scan_l.append(s.split(':')[1])
      if "Quality" in s:
         qualstr=s.split()
         scan_l.append(qualstr[0].split('=')[1])
         scan_l.append(qualstr[2].split('=')[1])
      if "ESSID" in s:
         scan_l.append(s.split(':')[1].strip('"'))
         scan_d[mac]=scan_l
         incell=False
         scan_l=[]
         print  "%s:%s" % (mac, scan_d[mac])
   return scan_d

if __name__ == '__main__':
   
   scan('wlan0') 
