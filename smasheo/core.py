import cv2
import numpy as np
import imutils
import argparse
from collections import deque
import Tkinter as tk
import threading
import playerInfo

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video")
args = vars(ap.parse_args())

vs = cv2.VideoCapture(args["video"])
frame_width = int(vs.get(3))
frame_height = int(vs.get(4))
fps = int(vs.get(5))
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#out = cv2.VideoWriter('outpy.avi',fourcc, fps, (frame_width,frame_height),1)

def run():
	def callback():
		while True:
			frame = vs.read()
			frame = frame[1]
			if frame is None:
				break



			#print(playerInfo.whatsYourDamage(frame,frame_width,frame_height))
			#playerInfo.getYourLifeOverMine(frame,frame_width,frame_height)

			#out.write(frame)
			key = cv2.waitKey(1) & 0xFF

			if key == ord("q"):
				break

		vs.release()
		#out.release()
		cv2.destroyAllWindows()
	t = threading.Thread(target=callback)
	t.start()
	return t;


r = tk.Tk()
r.title('Smasheo')

button = tk.Button(r, text='Run', width=25, command= run())
button.pack()
r.mainloop()
