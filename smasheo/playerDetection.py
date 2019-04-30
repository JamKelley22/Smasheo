import cv2
import numpy as np
import sys
import Complex
import fft
import test
import movingAvg as mv
import audioProcessing as ap
import stockDetection

dedePos = [];
#plat template: [x1, x2, y]
BIG_PLAT = [186, 1080, 555, 725]
S_L_PLAT = [285, 505, 415, 455]
S_M_PLAT = [520, 740, 286, 329]
S_R_PLAT = [750, 970, 415, 455]
UP_HAMM_AREA_MIN = 200000

width = 0
height = 0

def findCircles(mask, frm):
    circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1.2, 100)
    if circles is not None:
        for i in range(0, len(circles)):
            print circles[i]
            cv2.circle(frm, (circles[i][0], circles[i][1]), circles[i][2], (255, 0, 255), 2)
            cv2.imshow("circle", frm)

def drawLabel(frm, name, x, y, color):
    # cv2.rectangle(frm, (186, 555), (1080, 700), (255, 0, 0), 2)
    # cv2.rectangle(frm, (285, 415), (505, 485), (255, 0, 0), 2)
    # cv2.rectangle(frm, (520, 286), (740, 359), (255, 0, 0), 2)
    # cv2.rectangle(frm, (750, 415), (970, 485), (255, 0, 0), 2)
    cv2.putText(frm, name,(y, x),cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1, cv2.LINE_AA)
    return frm

def findTarget(bw, frm, name):
    comps, output, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)

    if len(stats) > 1:
        biggest = stats[1]
        for i in range(1, comps):
            if stats[i][4] > biggest[4]:
                biggest = stats[i]
        #cv2.putText(frm, name,(biggest[0], biggest[1]),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,100,100), 2, cv2.LINE_AA)
        return (biggest[0], biggest[1], biggest[2], biggest[3], name)
    return (0, 0, 0, 0, name)

def findBlueShield(frm):
    se = np.ones((5,5))
    low = (220, 230, 255)
    high = (255, 255, 255)
    #hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frm, low, high)
    #mask[0:150, 0:width] = 0
    mask[580:height, 240:1000] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "Blue Shield"), mask;

def findRedShield(frm):
    se = np.ones((2,2))
    low = (170, 50, 50)
    high = (255, 200, 250)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frm, low, high)
    #mask[0:150, 0:width] = 0
    mask[580:height, 240:1000] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((2,2)),iterations=8)
    return findTarget(mask, frm, "Blue Shield"), mask;


def findDK(frm):
    se = np.ones((6,6))
    low = (84, 47, 121)
    high = (189, 113, 235)
    #hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frm, low, high)
    #mask[0:150, 0:width] = 0
    mask[580:height, 240:1000] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((10,10)),iterations=8)
    return findTarget(mask, frm, "Donkey Kong");

def findDedede(frm):
    se = np.ones((6,6))
    low = (70, 50, 50)
    high = (130, 200, 250)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    # mask[0:150, 0:width] = 0
    mask[580:height, 240:1000] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "King Dedede"), mask;

def findKirby(frm):
    se = np.ones((6,6))
    low = (126, 84, 91)
    high = (255, 177, 210)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    #mask[0:150, 0:width] = 0
    mask[580:height, 240:1000] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "Kirby");

def findHammer(frm):
    se = np.ones((6,6))
    low = (17, 41, 92)
    high = (92, 165, 204)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    # mask[0:150, 0:width] = 0
    mask[580:height, 240:1000] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "Hammer");

def findGordo(frm):
    se = np.ones((6,6))
    low = (25, 37, 30)
    high = (54, 43, 66)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    mask[0:150, 0:width] = 0
    mask[600:height, 0:width] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "Gordo");

def findPlatforms(frm):
    se = np.ones((6,6))
    low = (26, 30, 40)
    high = (33, 89, 90)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    mask[0:150, 0:width] = 0
    mask[600:height, 0:width] = 0
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return mask#findTarget(mask, frm, "Platform");

def hideDK(frm, dkPos):
    #cv2.rectangle(frm, (dkPos[0], dkPos[1]), (dkPos[0] + dkPos[3], dkPos[1] + dkPos[2]), (0,0,0), cv2.FILLED)
    frm[dkPos[1]:dkPos[1] + dkPos[2], dkPos[0]:dkPos[0] + dkPos[3]] = (0,0,0)
    return frm

def drawAttack(frm):
    cv2.putText(frm, "Up smash",(120, 250),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,100,255), 2, cv2.LINE_AA)
    return frm

def drawPoint(frm, pos):
    frm[pos[1]:pos[1] + 5, pos[0]:pos[0] + 5] = (0, 255, 0)

def onPlatform(stats):
    x = stats[0]
    y = stats[1]
    len = stats[2]/2 - 10
    height = stats[3]
    endX = x + len
    endY = y + height
    #print endY
    if x >= BIG_PLAT[0] and endX <= BIG_PLAT[1] and endY >= BIG_PLAT[2] and y <= BIG_PLAT[3]:
        return True
    if x >= S_L_PLAT[0] and endX <= S_L_PLAT[1] and endY >= S_L_PLAT[2] and y <= S_L_PLAT[3]:
        return True
    if x >= S_M_PLAT[0] and endX <= S_M_PLAT[1] and endY >= S_M_PLAT[2] and y <= S_M_PLAT[3]:
        return True
    if x >= S_R_PLAT[0] and endX <= S_R_PLAT[1] and endY >= S_R_PLAT[2] and y <= S_R_PLAT[3]:
        return True
    return False
