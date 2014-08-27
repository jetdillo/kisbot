import sys
import subprocess
import re
import pdb
import time
from collections import deque,Counter

import numpy

import rospy
import roslib
import tf 
import geometry_msgs.msg
roslib.load_manifest('learning_tf')

from kisbot.msg import KisbotIWScanData
from kisbot.cfg import KisbotConfig as ConfigType



class IWMap():

   def __init__(self,iface):

      rospy.init_node('iwmap',KisbotIWMapScanData)      
      iw_listener=rospy.listener('iwscan',scanlistener)
      tf_listener=tf.TransformListener()
      rate=rospy.Rate(10.0)
            
 
   
