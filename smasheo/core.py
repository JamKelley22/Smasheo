import sys,os
import cv2
import numpy as np
import imutils
import argparse
from collections import deque
import Tkinter as tk
import threading
import curses
#import heatmap
import logging
try:
	import heatmap
except ImportError:
    print("Cannot import heatmap")

import playerInfo
import sys
import Complex
import fft
import test
import movingAvg as mv
import audioProcessing as audP
import stockDetection
import playerDetection as pd
import stats

#def checkWithinAcceptableLimit(avg, elem, movAvg):

def drawOutcome(frm, dedeChance, kirbyChance):
	return

def handleAttacks(upSmashes, timeStamp, hammerArea, dedeOnPlat, movesOnHold, doDrawAttack, labelFrame, attackFrame, count, dedePos):
	if (len(upSmashes) > 0 and timeStamp >= upSmashes[0]):
		time = upSmashes.pop(0)
		if (hammerArea >= pd.UP_HAMM_AREA_MIN and dedeOnPlat):
			doDrawAttacks = True
			attackFrame = count
			#print timeStamp, upSmashes[0]
		else:
			movesOnHold.append([0, time, count + 10])
	if (doDrawAttack):
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
	return upSmashes, timeStamp, hammerArea, dedeOnPlat, movesOnHold, doDrawAttack, labelFrame, attackFrame, count, dedePos

def trackObjects(frame, hammerAvg):
	dedePos, dMask = pd.findDedede(frame)
	kirbyPos = pd.findKirby(frame)
	#gordoPos = pd.findGordo(frame)
	#bsPos, bMask = pd.findRedShield(frame)
	labelFrame = pd.drawLabel(frame, dedePos[4], dedePos[1], dedePos[0], (0, 0, 255))
	labelFrame = pd.drawLabel(labelFrame, kirbyPos[4], kirbyPos[1], kirbyPos[0], (0, 0, 255))
	hammerPos = pd.findHammer(labelFrame)
	labelFrame = pd.drawLabel(labelFrame, hammerPos[4], hammerPos[1], hammerPos[0], (0, 0, 255))
	#labelFrame = pd.drawLabel(labelFrame, gordoPos[4], gordoPos[1], gordoPos[0], (0, 0, 255))
	#labelFrame = pd.drawLabel(labelFrame, bsPos[4], bsPos[1], bsPos[0], (0, 0, 255))
	hammerAvg.insert((hammerPos[0], hammerPos[1]))
	#cv2.imshow("red shield", bMask)
	return labelFrame, dedePos, hammerPos, kirbyPos, dMask

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

def drawText(stdscr,k,cursor_x,cursor_y,dmgD,dmgK,curStockD,curStockK,dChance,kChance):
	# Initialization
	stdscr.clear()
	height, width = stdscr.getmaxyx()

	if k == curses.KEY_DOWN:
		cursor_y = cursor_y + 1
	elif k == curses.KEY_UP:
		cursor_y = cursor_y - 1
	elif k == curses.KEY_RIGHT:
		cursor_x = cursor_x + 1
	elif k == curses.KEY_LEFT:
		cursor_x = cursor_x - 1

	cursor_x = max(0, cursor_x)
	cursor_x = min(width-1, cursor_x)

	cursor_y = max(0, cursor_y)
	cursor_y = min(height-1, cursor_y)

	# Declaration of strings
	title = "Smasheo"
	subtitle = "Smash Ultmate Video Analizer"[:width-1]
	keystr = "Last key pressed: {}".format(k)[:width-1]
	statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)
	if k == 0:
		keystr = "No key press detected..."[:width-1]
	#print dmgD, dmgK, curStockD, curStockK, dChance, kChance
	dmgK_s = "Damage: {}%".format(str(dmgK).ljust(3))
	dmgD_s = "Damage: {}%".format(str(dmgD).ljust(3))
	currStockD_s = "Stock: {}".format(curStockD)
	currStockK_s = "Stock: {}".format(curStockK)
	dChance_s = "Chance: {}%".format(dChance)
	kChance_s = "Chance: {}%".format(kChance)

	# Centering calculations
	start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
	start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
	start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
	start_y = int((height // 2) - 2)

	start_x_left = int((width // 3) - (len(dmgD_s) // 2) - len(dmgD_s) % 2)
	start_x_right = (width - int((width // 3)) - (len(dmgD_s) // 2) - len(dmgD_s) % 2)

	# Rendering some text
	#whstr = "Width: {}, Height: {}".format(width, height)
	#stdscr.addstr(0, 0, whstr, curses.color_pair(1))

	# Render status bar
	stdscr.attron(curses.color_pair(3))
	stdscr.addstr(height-1, 0, statusbarstr)
	stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
	stdscr.attroff(curses.color_pair(3))

	# Turning on attributes for title
	stdscr.attron(curses.color_pair(2))
	stdscr.attron(curses.A_BOLD)

	# Rendering title
	stdscr.addstr(0, start_x_title, title)

	# Turning off attributes for title
	stdscr.attroff(curses.color_pair(2))
	stdscr.attroff(curses.A_BOLD)

	# Print rest of text
	stdscr.addstr(1, start_x_subtitle, subtitle)
	#stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
	#stdscr.addstr(start_y + 5, start_x_keystr, keystr)
	#left
	stdscr.attron(curses.color_pair(1))
	stdscr.addstr(start_y, start_x_left, "Kirby")
	stdscr.attroff(curses.color_pair(1))
	stdscr.addstr(start_y+1, start_x_left, dmgK_s)
	stdscr.addstr(start_y+2, start_x_left, currStockK_s)
	stdscr.addstr(start_y+3, start_x_left, kChance_s)

	#Right
	stdscr.attron(curses.color_pair(1))
	stdscr.addstr(start_y, start_x_right, "King Dedede")
	stdscr.attroff(curses.color_pair(1))
	stdscr.addstr(start_y+1, start_x_right, dmgD_s)
	stdscr.addstr(start_y+2, start_x_right, currStockD_s)
	stdscr.addstr(start_y+3, start_x_right, dChance_s)

	stdscr.move(cursor_y, cursor_x)

	# Refresh the screen
	stdscr.refresh()

def smash(stdscr,brian):
	k = 0
	if(stdscr != None):
		cursor_x = 0
		cursor_y = 0

	    # Clear and refresh the screen for a blank canvas
		stdscr.clear()
		stdscr.refresh()

	    # Start colors in curses
		curses.start_color()
		curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
		stdscr.nodelay(1)#getch is non-blocking

	tracker = 0

	ap = argparse.ArgumentParser()
	ap.add_argument("-v", "--video")
	args = vars(ap.parse_args())

	if(args["video"] == None):
		sys.exit("Must specify video file with -v option")

	vs = cv2.VideoCapture(args["video"])
	frame_width = int(vs.get(3))
	frame_height = int(vs.get(4))
	fps = int(vs.get(5))
	fourcc = cv2.VideoWriter_fourcc('M','J','P','G')

	upSmashes = [4386749362,238792366]#audP.main()
	width = int(vs.get(3))
	height = int(vs.get(4))
	pd.width = width
	pd.height = height
	count = 0
	attackFrame = 0
	doDrawAttack = False
	hammerAvg = mv.MovingAvg(0, 10)
	dedeAvg = mv.MovingAvg(0, 5)
	            #ID, time, timeout
	movesOnHold = []
	curStockD = 0
	curStockK = 0
	initStock = 0

	dededeAirTime = 0
	kirbyAirTime = 0

	dededeKOTime = []
	kirbyKOTime = []
	curDededeTime = 0
	curKirbyTime = 0

	initFrame = None
	kPosArr = []
	dPosArr = []
	if (not brian):
		hm = heatmap.Heatmap()

	actionFrames = deque([])
	lastDStock = 2
	lastKStock = 2

    # Loop where k is the last character pressed
	while (k != ord('q')):

		frame = vs.read()
		frame = frame[1]
		if frame is None:
			break

		if count == 0:
			initFrame = frame

		timeStamp = count * 16.6667

		labelFrame, dedePos, hammerPos, kirbyPos, dMask = trackObjects(frame, hammerAvg)

		if(count % 5 == 0):
			kPosArr.append((kirbyPos[0],frame_height - kirbyPos[1]))
			dPosArr.append((dedePos[0],frame_height - dedePos[1]))#Why???

		if(not brian):
			if(count % 20 == 0):
				dHeatmap = hm.heatmap(dPosArr,scheme='fire',size=(frame_width, frame_height))
				kHeatmap = hm.heatmap(kPosArr,scheme='pbj',size=(frame_width, frame_height))

				dHeatmap = cv2.cvtColor(np.array(dHeatmap), cv2.COLOR_RGB2BGR)
				kHeatmap = cv2.cvtColor(np.array(kHeatmap), cv2.COLOR_RGB2BGR)
				heatmapCombined = dHeatmap #+ kHeatmap
		#cv2.imshow("h1",opencvImage)

		dmg = playerInfo.whatsYourDamage(frame,frame_width,frame_height)
		dmgD = damageToInt(dmg[0])
		dmgK = damageToInt(dmg[1])
		prevStockD = curStockD
		prevStockK = curStockK
		curStockD, curStockK = trackStock(curStockD, curStockK, labelFrame, count)
		print curStockD, curStockK
		if (prevStockD <= curStockD):
			dif = 0
			if (len(dededeKOTime) == 0):
				dif = count
			else:
				dif = count - dededeKOTime[len(dededeKOTime) - 1]
			dededeKOTime.append(dif)
			if count > 10:
				actionFrames.appendleft(count)

		if (prevStockK <= curStockK):
			dif = 0
			if (len(kirbyKOTime) == 0):
				dif = count
			else:
				dif = count - kirbyKOTime[len(kirbyKOTime) - 1]
			kirbyKOTime.append(dif)
			if count > 10:
				actionFrames.appendleft(count)



		dChance, kChance = stats.guessProspects(initStock, curStockD, curStockK, dmgD, dmgK)

		print dmgD, dmgK, curStockD, curStockK, dChance, kChance

		if (count == 0):
			initStock = curStockD
			lastDStock = curStockD

		hammerArea = hammerAvg.area()
		dedeOnPlat = pd.onPlatform(dedePos)
		kirbyOnPlat = pd.onPlatform(kirbyPos)
		upSmashes, timeStamp, hammerArea, dedeOnPlat, movesOnHold, doDrawAttack, labelFrame, attackFrame, count, dedePos = handleAttacks(upSmashes, timeStamp, hammerArea, dedeOnPlat, movesOnHold, doDrawAttack, labelFrame, attackFrame, count, dedeAvg)
		#print(timeStamp)
		if (dedeOnPlat == False):
			dededeAirTime += 1
		if (kirbyOnPlat == False):
			kirbyAirTime += 1

		dedeString = "King Dedede: Win Chance: " + str(dChance) + "% Air Time " + str(np.round(dededeAirTime * 16.677) / 1000) + "s Ground Attack?: " + str(doDrawAttack) + " Stock: " + str(curStockD)
		kirbyString = "Kirby: Win Chance: " + str(kChance) + "% Air Time " + str(np.round(kirbyAirTime * 16.677) / 1000) + "s Ground Attack?: N/A Stock: " + str(curStockK)
		pd.drawLabel(frame, dedeString, 100, 10, (200, 200, 200))
		pd.drawLabel(frame, kirbyString, 150, 10, (200, 200, 200))

		#print stats.guessProspects(initStock, curStockD, curStockK, )
		# for i in range(0, len(hammerAvg.getSet())):
		# 	pd.drawPoint(labelFrame, hammerAvg.getSet()[i])
		#dedeFrame = cv2.cvtColor(dedeFrame, cv2.COLOR_BGR2HSV)
		if(not brian):
			heatSuper = cv2.addWeighted(labelFrame, 0.7, heatmapCombined, 0.3, 0)
			cv2.imshow("Video", heatSuper)
		else:
			cv2.imshow("Video", labelFrame)

		#cv2.imshow("Video", labelFrame)
		#cv2.imshow("bw", dMask)


		lastDStock = curStockD
		lastKStock = curStockK

		#if count > 1:
			#print (float(tracker)/count)*100
		#out.write(frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord("q"):
			break
		elif key == ord("t"):
			tracker += 1

		if(stdscr != None):
			drawText(stdscr,k,cursor_x,cursor_y,dmgD,dmgK,curStockD,curStockK,dChance,kChance)
			k = stdscr.getch()

		count += 1

	print np.sum(tracker), count

	#==============Compile Highlights
	out = cv2.VideoWriter('highlights.avi',fourcc, fps, (frame_width,frame_height),1)

	vs_out = cv2.VideoCapture(args["video"])
	count_out = 0
	if actionFrames:
		nextFrame = actionFrames.pop()
	else:
		vs_out.release()
		vs.release()
		sys.exit()

	slice_thresh = 30
	print("Action Frames")
	print(actionFrames)
	while(vs_out.isOpened()):
		frame_out = vs_out.read()
		frame_out = frame_out[1]
		if abs(nextFrame - count_out < slice_thresh):
			out.write(frame_out)
			if actionFrames:
				nextFrame = actionFrames.pop()
			else:
				break
		if nextFrame <= count_out:
			if actionFrames:
				nextFrame = actionFrames.pop()
			else:
				break

		count_out += 1
		print(count_out)

	vs_out.release()
	vs.release()

def initLogger():
	logger = logging.getLogger(__file__)
	hdlr = logging.FileHandler(__file__ + ".log")
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr)
	logger.setLevel(logging.DEBUG)
	#logger.info("begin")
	return logger

def main():
	dev = True
	brian = True #Set this insted of commenting heatmap
	global logger
	logger = initLogger()

	if(not dev):
		SCREEN = curses.initscr()
		smash(SCREEN,brian)
	else:
		smash(None,brian)
	cv2.destroyAllWindows()

main()
