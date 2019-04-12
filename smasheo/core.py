import cv2
import numpy as np
import imutils
import argparse
from collections import deque

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video")
args = vars(ap.parse_args())

vs = cv2.VideoCapture(args["video"])
frame_width = int(vs.get(3))
frame_height = int(vs.get(4))
fps = int(vs.get(5))
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#out = cv2.VideoWriter('outpy.avi',fourcc, fps, (frame_width,frame_height),1)
lower_red = np.array([0,100,100])
upper_red = np.array([5,255,255])

search_nums = [0,1,2,3,4,5,6,7,8,9]

struct_nums_l = [None] * len(search_nums)

for i,num in enumerate(search_nums):
	print(str(num))
	loc = 'structuring_elements/numbers/large/%s.png' % str(num)
	struct_nums_l[i] = cv2.imread(loc,0)
	struct_nums_l[i] = cv2.erode(struct_nums_l[i], np.ones((3,3),np.uint8),iterations = 2)
'''
for i, struct_num in enumerate(struct_nums):
	struct_nums[i] = cv2.erode(struct_num, np.ones((3,3),np.uint8),iterations = 1)
'''

threshold_val_low = 65
threshold_val = 120

cnt = 1

while True:
	cnt += 1
	
	frame = vs.read()
	
	frame = frame[1]
	if frame is None:
		break
		
	frameL = frame[610:frame_height-55,335:frame_width-825]
	frameR = frame[610:frame_height-55,830:frame_width-335]
		
	#hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	
	grayL = cv2.cvtColor(frameL, cv2.COLOR_BGR2GRAY)
	grayR = cv2.cvtColor(frameR, cv2.COLOR_BGR2GRAY)
	
	retvalL, thresholdL = cv2.threshold(grayL, threshold_val, 255, cv2.THRESH_BINARY)
	retvalR, thresholdR = cv2.threshold(grayR, threshold_val, 255, cv2.THRESH_BINARY)
	
	thresholdL = cv2.morphologyEx(thresholdL, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
	thresholdR = cv2.morphologyEx(thresholdR, cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
	
	openL = cv2.morphologyEx(thresholdL, cv2.MORPH_OPEN, struct_nums_l[0])
	for s in struct_nums_l:
		#cv2.imshow('s',s)
		openL += cv2.morphologyEx(thresholdL, cv2.MORPH_OPEN, s)
		#print(openL.shape)
		#thresholdL = thresholdL - openL;
	
	numpy_horizontal_concat = np.concatenate((openL, thresholdL), axis=1)
	cv2.imshow('res',numpy_horizontal_concat)
	
	#out.write(frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break
		
vs.release()
#out.release()
cv2.destroyAllWindows()
