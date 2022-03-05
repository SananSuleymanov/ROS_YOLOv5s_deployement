#!/usr/bin/env python3

"""
Node for Diver tracking control

@authors:
@contact:
"""

import rospy
import numpy as np
import cv2    # This imports openCV library
from cv_bridge import CvBridge, CvBridgeError
from ProcessImage import ProcessImage
from sensor_msgs.msg import Image
import os


import torch

model = torch.hub.load('ultralytics/yolov5', 'custom', '/home/sanan/catkin_ws/src/UCAT_UUV/ucat_autonomy/scripts/best.pt')


class DiverTracking:
	def __init__(self, rate):
		self.rate = rospy.Rate(rate)
		self.dt = 1.0 / rate
		self.camera_sub = rospy.Subscriber("/ucat/camera/camera_image", Image, self.step) #don't use self.step as callback 
		self.bridge = CvBridge()
		
	

	def step(self, image):
		
		ros_image = self.bridge.imgmsg_to_cv2(image, "bgr8")
		self.image = ros_image
		result = model(self.image)
		#print(result.xyxy[0].numpy())
		xmin = int(result.xyxy[0].numpy()[0][0])
		ymin = int(result.xyxy[0].numpy()[0][1])
		xmax = int(result.xyxy[0].numpy()[0][2])
		ymax = int(result.xyxy[0].numpy()[0][3])
		mAp = float(result.xyxy[0].numpy()[0][4])
		obj = int(result.xyxy[0].numpy()[0][5])
		
		
		print('xmin: '+str(xmin), 'ymin: ' +str(ymin), 'xmax: ' +str(xmax), 'ymax: '+ str(ymax))
		print('mAp: '+ str(mAp))
		if obj == 0:
		  print('Class: Diver')
		
		start_point= (xmin, ymin)
		end_point = (xmax, ymax)
		cv2.rectangle(self.image, start_point, end_point, (255, 0, 0), 2)
		cv2.putText(self.image, 'Diver', (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
		cv2.imshow('Image', self.image)
		
		if cv2.waitKey(1) & 0xFF == ord('q'):
		  cv2.destroyAllWindows()
		
		pass

	def run(self):
		"""
		Main loop of class.
		@param: self
		"""
		while not rospy.is_shutdown():
		        
			self.rate.sleep()


if __name__=="__main__":
	rospy.init_node("DiverTrackingController")
	diverTracking = DiverTracking(20.0) # (rate)
	diverTracking.run()
