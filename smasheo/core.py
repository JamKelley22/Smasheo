import cv2
import numpy as np
import imutils
import argparse
from collections import deque
import damage

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video")
args = vars(ap.parse_args())

vs = cv2.VideoCapture(args["video"])
frame_width = int(vs.get(3))
frame_height = int(vs.get(4))
fps = int(vs.get(5))
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#out = cv2.VideoWriter('outpy.avi',fourcc, fps, (frame_width,frame_height),1)

while True:
	frame = vs.read()
	frame = frame[1]
	if frame is None:
		break

	print(damage.whatsYourDamage(frame,frame_width,frame_height))

	#out.write(frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

vs.release()
#out.release()
cv2.destroyAllWindows()
