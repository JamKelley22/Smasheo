import cv2
import numpy as np
import sys
import Complex
import fft
import test
import movingAvg as mv
import audioProcessing as ap

dedePos = [];

def drawLabel(frm, name, x, y, color):
    cv2.putText(frm, name,(y, x),cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
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

def findDK(frm):
    se = np.ones((6,6))
    low = (84, 47, 121)
    high = (189, 113, 235)
    #hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(frm, low, high)
    mask[0:150, 0:width] = 0
    mask[600:height, 0:width] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((10,10)),iterations=8)
    return findTarget(mask, frm, "Donkey Kong");

def findDedede(frm):
    se = np.ones((6,6))
    low = (70, 50, 50)
    high = (130, 200, 250)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    mask[0:150, 0:width] = 0
    mask[600:height, 0:width] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "King Dedede");

def findHammer(frm):
    se = np.ones((6,6))
    low = (17, 60, 92)
    high = (92, 165, 204)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    mask[0:150, 0:width] = 0
    mask[600:height, 0:width] = 0
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "Hammer");

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

clips = ['../replays/replay1.mp4']
for i in range(len(clips)):
    upSmashes = ap.main()#test.main()
    vid = cv2.VideoCapture(clips[i])
    width = int(vid.get(3))
    height = int(vid.get(4))
    fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
    title = "output" + str(i) + ".mp4"
    writer = cv2.VideoWriter(title, fourcc,60.0,(width, height))
    count = 0
    attackFrame = 0
    doDrawAttack = False
    hammerAvg = mv.MovingAvg(0, 10)
    while(vid.isOpened()):
        val, frm = vid.read()
        if val == True:
            cv2.waitKey(17)
            timeStamp = count * 16.6667
            bw = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
            dummy, bw = cv2.threshold(bw, 100, 255, cv2.THRESH_BINARY)
            dedePos = findDedede(frm)
            dkPos = findDK(frm)
            platPos = findPlatforms(frm)
            labelFrame = drawLabel(frm, dedePos[4], dedePos[1], dedePos[0], (0, 0, 255))
            labelFrame = drawLabel(labelFrame, dkPos[4], dkPos[1], dkPos[0], (0, 0, 255))
            #labelFrame = drawLabel(labelFrame, platPos[4], platPos[1], platPos[0], (0, 0, 255))
            clone = np.copy(labelFrame)
            hideDKFrm = hideDK(frm, dkPos)
            hammerPos = findHammer(hideDKFrm)
            labelFrame = drawLabel(clone, hammerPos[4], hammerPos[1], hammerPos[0], (0, 0, 255))

            hammerAvg.insert((hammerPos[0], hammerPos[1]))
            #hammerAvg.printSet()
            displacement = hammerAvg.getDisplacement()
            dX = displacement[0]
            dY = displacement[1]
            # if dY < 7 and dY > -7 and dX > 30:
            #     doDrawAttack = True
            #     attackFrame = count

            for i in range(0, len(hammerAvg.getSet())):
                drawPoint(labelFrame, hammerAvg.getSet()[i])
            #dedeFrame = cv2.cvtColor(dedeFrame, cv2.COLOR_BGR2HSV)

            if (len(upSmashes) > 0 and timeStamp >= upSmashes[0]):
                upSmashes.pop(0)
                doDrawAttack = True
                attackFrame = count
                print timeStamp, upSmashes[0]
            if (doDrawAttack):
                labelFrame = drawAttack(labelFrame)
                if (count - attackFrame >= 30):
                    doDrawAttack = False

            cv2.imshow("Video", labelFrame)
            if cv2.waitKey(10) == 27:
                break

            count += 1
            writer.write(labelFrame)
            if (cv2.waitKey(25) & 0xFF == ord('q')):
                break
        else:
            break;
    vid.release()
    writer.release()
    cv2.destroyAllWindows()
