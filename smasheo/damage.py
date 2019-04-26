import cv2
import numpy as np
import imutils
import argparse
from collections import deque

search_nums = [0,1,3,2,8,4,9,6,5,7]
struct_nums_l = [None] * len(search_nums)

for i,num in enumerate(search_nums):
	loc = 'structuring_elements/numbers/large/%s.png' % str(num)
	struct_nums_l[i] = cv2.imread(loc,0)
	struct_nums_l[i] = cv2.erode(struct_nums_l[i], np.ones((3,3),np.uint8),iterations = 3)

threshold_val = 110

def whatsYourDamage(frame,frame_width,frame_height):
	frameL = frame[610:frame_height-55,335:frame_width-825]
	frameR = frame[610:frame_height-55,830:frame_width-335]

	hsvL = cv2.cvtColor(frameL, cv2.COLOR_BGR2HSV)
	hsvR = cv2.cvtColor(frameR, cv2.COLOR_BGR2HSV)

	grayL = cv2.cvtColor(frameL, cv2.COLOR_BGR2GRAY)
	grayR = cv2.cvtColor(frameR, cv2.COLOR_BGR2GRAY)

	retvalL, thresholdL = cv2.threshold(grayL, threshold_val, 255, cv2.THRESH_BINARY)
	retvalR, thresholdR = cv2.threshold(grayR, threshold_val, 255, cv2.THRESH_BINARY)

	thresholdL = cv2.morphologyEx(thresholdL, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
	thresholdR = cv2.morphologyEx(thresholdR, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))


	#========================================
	lower_red_low = np.array([0,50,50])
	upper_red_low = np.array([10,255,255])
	lower_red_up = np.array([170,50,50])
	upper_red_up = np.array([180,255,255])

	mask0L = cv2.inRange(hsvL, lower_red_low, upper_red_low)
	mask1L = cv2.inRange(hsvL, lower_red_up, upper_red_up)

	mask0R = cv2.inRange(hsvR, lower_red_low, upper_red_low)
	mask1R = cv2.inRange(hsvR, lower_red_up, upper_red_up)

	maskL = mask0L+mask1L
	maskR = mask0R+mask1R

	maskL = cv2.morphologyEx(maskL, cv2.MORPH_OPEN, np.ones((3,3),np.uint8),iterations=2)
	maskR = cv2.morphologyEx(maskR, cv2.MORPH_OPEN, np.ones((3,3),np.uint8),iterations=2)
	thresholdL = thresholdL + maskL
	thresholdR = thresholdR + maskR
	#=====================================

	openL = cv2.morphologyEx(thresholdL, cv2.MORPH_OPEN, struct_nums_l[0])
	openR = cv2.morphologyEx(thresholdR, cv2.MORPH_OPEN, struct_nums_l[0])

	leftNums = [-1,-1,-1]
	rightNums = [-1,-1,-1]

	leftNumPos = [[27,17],[27,47],[27,82]]
	rightNumPos = [[27,17],[27,47],[27,82]]

	eL = 0
	eR = 0
	for i, s in enumerate(struct_nums_l):
		eL += cv2.erode(thresholdL, s)
		eR += cv2.erode(thresholdR, s)
		eL = cv2.dilate(eL, np.ones((3,3),np.uint8))
		eR = cv2.dilate(eR, np.ones((3,3),np.uint8))
		#cv2.imshow('e',eR[25:30,80:85])
		#print(eR[27,82])
		for numPosGet in range(0,3):
			leftPosIntensity = eL[leftNumPos[numPosGet][0],leftNumPos[numPosGet][1]]
			#print(leftPosIntensity)
			if(leftPosIntensity == 255 and leftNums[numPosGet] == -1):
				#print(numPosGet)
				leftNums[numPosGet] = search_nums[i]

		for numPosGet in range(0,3):
			rightPosIntensity = eR[rightNumPos[numPosGet][0],rightNumPos[numPosGet][1]]
			if(rightPosIntensity == 255 and rightNums[numPosGet] == -1):
				rightNums[numPosGet] = search_nums[i]

		s = cv2.flip(cv2.flip(s,flipCode=0), flipCode=1)

		openL += cv2.dilate(eL, s)
		openR += cv2.dilate(eR, s)
		#openL += cv2.morphologyEx(thresholdL, cv2.MORPH_OPEN, s)
		#thresholdL = thresholdL - openL;

	out_nums = [leftNums,rightNums]#str(leftNums) + '\t' + str(rightNums)
	#print(out_nums)
	leftNums = [-1,-1,-1]
	rightNums = [-1,-1,-1]

	#numpy_horizontal_concat = np.concatenate((openL, openR), axis=1)
	numpy_horizontal_concat_norm = np.concatenate((frameL, frameR), axis=1)
	#numpy_horizontal_concat_thresh = np.concatenate((thresholdL, thresholdR), axis=1)
	#numpy_horizontal_concat_hsv = np.concatenate((hsvL, hsvR), axis=1)
	#numpy_horizontal_concat_isocolor = np.concatenate((redsL, redsR), axis=1)
	#numpy_horizontal_concat_erode = np.concatenate((eL, eR), axis=1)

	#cv2.imshow('res',numpy_horizontal_concat)
	#cv2.imshow('norm',numpy_horizontal_concat_norm)
	#cv2.imshow('thresh',numpy_horizontal_concat_thresh)
	#cv2.imshow('erode',numpy_horizontal_concat_erode)
	#cv2.imshow('hsv',numpy_horizontal_concat_hsv)
	#cv2.imshow('isocolor',numpy_horizontal_concat_isocolor)

	return out_nums
