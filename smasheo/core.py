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
import stats

def handleAttacks(upSmashes, timeStamp, hammerArea, dedeOnPlat, movesOnHold, doDrawAttack, labelFrame, attackFrame):
	if (len(upSmashes) > 0 and timeStamp >= upSmashes[0]):
		time = upSmashes.pop(0)
		if (hammerArea >= pd.UP_HAMM_AREA_MIN and dedeOnPlat):
			doDrawAttacks = True
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
		if (hammerArea >= pd.UP_HAMM_AREA_MIN and dedeOnPlat):
			doDrawAttack = True
			attackFrame = count
		elif count > held[2]:
			removeLater.append(movesOnHold[i])
	for i in range(0, len(removeLater)):
		movesOnHold.remove(removeLater[i])

def trackObjects(frame, hammerAvg):
	dedePos, dMask = pd.findDedede(frame)
	kirbyPos = pd.findKirby(frame)
	gordoPos = pd.findGordo(frame)
	labelFrame = pd.drawLabel(frame, dedePos[4], dedePos[1], dedePos[0], (0, 0, 255))
	labelFrame = pd.drawLabel(labelFrame, kirbyPos[4], kirbyPos[1], kirbyPos[0], (0, 0, 255))
	hammerPos = pd.findHammer(labelFrame)
	labelFrame = pd.drawLabel(labelFrame, hammerPos[4], hammerPos[1], hammerPos[0], (0, 0, 255))
	labelFrame = pd.drawLabel(labelFrame, gordoPos[4], gordoPos[1], gordoPos[0], (0, 0, 255))
	hammerAvg.insert((hammerPos[0], hammerPos[1]))
	return labelFrame, dedePos, kirbyPos, hammerPos

def trackStock(curStockD, curStockK, labelFrame, count):
	frmStockD = stockDetection.getDededeStock(labelFrame)
	frmStockK = stockDetection.getKirbyStock(labelFrame)
	if (frmStockD != -1 and frmStockD <= curStockD) or count == 0:
		curStockD = frmStockD
	if (frmStockK != -1 and frmStockK <= curStockK) or count == 0:
		curStockK = frmStockK
	return curStockD, curStockK

def damageToInt(dam):
	incr = 1
	num = 0
	for i in range(len(dam)-1, 0, -1):
		if dam[i] != -1:
			num += incr * dam[i]
		incr *= 10
	return num

def main():
	tracker = []

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
	width = int(vs.get(3))
	height = int(vs.get(4))
	pd.width = width
	pd.height = height
	count = 0
	attackFrame = 0
	doDrawAttack = False
	hammerAvg = mv.MovingAvg(0, 10)
	dedeAvg = mv.MovingAvg(0, 10)
	            #ID, time, timeout
	movesOnHold = []
	curStockD = 0
	curStockK = 0
	initStock = 0
	while True:
		frame = vs.read()
		frame = frame[1]
		if frame is None:
			break

		cv2.waitKey(17)
		timeStamp = count * 16.6667

		labelFrame, dedePos, hammerPos, kirbyPos = trackObjects(frame, hammerAvg)

		dmg = damage.whatsYourDamage(frame,frame_width,frame_height)
		dmgD = damageToInt(dmg[0])
		dmgK = damageToInt(dmg[1])
		curStockD, curStockK = trackStock(curStockD, curStockK, labelFrame, count)
		dChance, kChance = stats.guessProspects(initStock, curStockD, curStockK, dmgD, dmgK)
		print dmgD, dmgK, curStockD, curStockK, dChance, kChance

		if (count == 0):
			initStock = curStockD
		hammerArea = hammerAvg.area()
		dedeOnPlat = pd.onPlatform(dedePos)
		handleAttacks(upSmashes, timeStamp, hammerArea, dedeOnPlat, movesOnHold, doDrawAttack, labelFrame, attackFrame)
		#print stats.guessProspects(initStock, curStockD, curStockK, )
		# for i in range(0, len(hammerAvg.getSet())):
		# 	pd.drawPoint(labelFrame, hammerAvg.getSet()[i])
		#dedeFrame = cv2.cvtColor(dedeFrame, cv2.COLOR_BGR2HSV)


		cv2.imshow("Video", labelFrame)

		count += 1
		#writer.write(labelFrame)
		if (cv2.waitKey(25) & 0xFF == ord('q')):
			break

		# if (cv2.waitKey(25) & 0xFF == ord('t')):
		# 	tracker.append("1")
		# else:
		# 	tracker.append("0")

		#print tracker
		#out.write(frame)
		key = cv2.waitKey(1) & 0xFF

		if key == ord("q"):
			break

	print np.sum(tracker), count
	vs.release()
	#out.release()
	cv2.destroyAllWindows()

main()
