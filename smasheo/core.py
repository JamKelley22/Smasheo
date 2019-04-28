import cv2
import numpy as np
import imutils
import argparse
from collections import deque
import damage
import sys
import Complex
import fft
import test
import movingAvg as mv
import audioProcessing as ap
import stockDetection
import playerDetection as pd


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video")
args = vars(ap.parse_args())

vs = cv2.VideoCapture(args["video"])
frame_width = int(vs.get(3))
frame_height = int(vs.get(4))
fps = int(vs.get(5))
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
#out = cv2.VideoWriter('outpy.avi',fourcc, fps, (frame_width,frame_height),1)

upSmashes = [50096, 649683]#ap.main()
width = int(vid.get(3))
height = int(vid.get(4))
count = 0
attackFrame = 0
doDrawAttack = False
hammerAvg = mv.MovingAvg(0, 10)
            #ID, time, timeout
movesOnHold = []
curStockD = 0
curStockK = 0

while True:
	frame = vs.read()
	frame = frame[1]
	if frame is None:
		break

	print(damage.whatsYourDamage(frame,frame_width,frame_height))
	cv2.waitKey(17)
	timeStamp = count * 16.6667
	bw = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
	dummy, bw = cv2.threshold(bw, 100, 255, cv2.THRESH_BINARY)
	dedePos, dMask = findDedede(frm)
	kirbyPos = pd.findKirby(frm)
	gordoPos = pd.findGordo(frm)
	labelFrame = pd.drawLabel(frm, dedePos[4], dedePos[1], dedePos[0], (0, 0, 255))
	labelFrame = pd.drawLabel(labelFrame, kirbyPos[4], kirbyPos[1], kirbyPos[0], (0, 0, 255))
	hammerPos = pd.findHammer(labelFrame)
	labelFrame = pd.drawLabel(labelFrame, hammerPos[4], hammerPos[1], hammerPos[0], (0, 0, 255))
	labelFrame = pd.drawLabel(labelFrame, gordoPos[4], gordoPos[1], gordoPos[0], (0, 0, 255))
	hammerAvg.insert((hammerPos[0], hammerPos[1]))
	displacement = hammerAvg.getDisplacement()
	dX = displacement[0]
	dY = displacement[1]

	frmStockD = stockDetection.getDededeStock(labelFrame)
	frmStockK = stockDetection.getKirbyStock(labelFrame)
	if (frmStockD != -1 and frmStockD <= curStockD) or count == 0:
		curStockD = frmStockD
	if (frmStockK != -1 and frmStockK <= curStockK) or count == 0:
		curStockK = frmStockK
	print curStockD, curStockK
	hammerArea = hammerAvg.area()
	for i in range(0, len(hammerAvg.getSet())):
		pd.drawPoint(labelFrame, hammerAvg.getSet()[i])
	#dedeFrame = cv2.cvtColor(dedeFrame, cv2.COLOR_BGR2HSV)

	dedeOnPlat = pd.onPlatform(dedePos)
	#print movesOnHold, hammerArea, dedeOnPlat
	if (len(upSmashes) > 0 and timeStamp >= upSmashes[0]):
		time = upSmashes.pop(0)
		if (hammerArea >= UP_HAMM_AREA_MIN and dedeOnPlat):
			doDrawAttack = True
			attackFrame = count
			#print timeStamp, upSmashes[0]
		else:
			movesOnHold.append([0, time, count + 10])
	if (doDrawAttack):
		labelFrame = pd.drawAttack(labelFrame)
		if (count - attackFrame >= 30):
			doDrawAttack = False

	removeLater = []
	for i in range(0, len(movesOnHold)):
		held = movesOnHold[i]
		if (hammerArea >= UP_HAMM_AREA_MIN and dedeOnPlat):
			doDrawAttack = True
			attackFrame = count
		elif count > held[2]:
			removeLater.append(movesOnHold[i])
	for i in range(i, len(removeLater)):
		movesOnHold.remove(removeLater[i])

	cv2.imshow("Video", labelFrame)
	cv2.imshow("bw", dMask)

	count += 1
	writer.write(labelFrame)
	if (cv2.waitKey(25) & 0xFF == ord('q')):
		break

	#out.write(frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord("q"):
		break

vs.release()
#out.release()
cv2.destroyAllWindows()
