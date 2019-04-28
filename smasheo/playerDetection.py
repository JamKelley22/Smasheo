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
BIG_PLAT = [196, 1080, 560, 600]
S_L_PLAT = [305, 505, 430, 485]
S_M_PLAT = [540, 740, 303, 359]
S_R_PLAT = [770, 970, 430, 485]

UP_HAMM_AREA_MIN = 200000

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
    return findTarget(mask, frm, "King Dedede"), mask;

def findKirby(frm):
    se = np.ones((6,6))
    low = (126, 84, 91)
    high = (255, 167, 200)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    mask[0:150, 0:width] = 0
    mask[600:height, 0:width] = 0
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se)
    mask = cv2.dilate(mask, np.ones((5,5)),iterations=8)
    return findTarget(mask, frm, "Kirby");

def findHammer(frm):
    se = np.ones((6,6))
    low = (17, 41, 92)
    high = (92, 165, 204)
    hsv = cv2.cvtColor(frm, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, low, high)
    mask[0:150, 0:width] = 0
    mask[600:height, 0:width] = 0
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
    len = stats[2]
    height = stats[3]
    endX = x + len
    endY = y + height
    #print endY
    if x >= BIG_PLAT[0] and endX <= BIG_PLAT[1] and endY >= BIG_PLAT[2] and endY <= BIG_PLAT[3]:
        return True
    if x >= S_L_PLAT[0] and endX <= S_L_PLAT[1] and endY >= S_L_PLAT[2] and endY <= S_L_PLAT[3]:
        return True
    if x >= S_M_PLAT[0] and endX <= S_M_PLAT[1] and endY >= S_M_PLAT[2] and endY <= S_M_PLAT[3]:
        return True
    if x >= S_R_PLAT[0] and endX <= S_R_PLAT[1] and endY >= S_R_PLAT[2] and endY <= S_R_PLAT[3]:
        return True
    return False

clips = ['../replays/replay4.mp4']
for i in range(len(clips)):
    upSmashes = [50096, 649683]#ap.main()
    vid = cv2.VideoCapture(clips[i])
    width = int(vid.get(3))
    height = int(vid.get(4))
    fps = int(vid.get(5))
    fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
    title = "output" + str(i) + ".mp4"
    writer = cv2.VideoWriter(title, fourcc,fps,(width, height))
    count = 0
    attackFrame = 0
    doDrawAttack = False
    hammerAvg = mv.MovingAvg(0, 10)
                #ID, time, timeout
    movesOnHold = []
    curStockD = 0
    curStockK = 0
    while(vid.isOpened()):
        val, frm = vid.read()
        if val == True:
            cv2.waitKey(17)
            timeStamp = count * 16.6667
            bw = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
            dummy, bw = cv2.threshold(bw, 100, 255, cv2.THRESH_BINARY)
            dedePos, dMask = findDedede(frm)
            kirbyPos = findKirby(frm)
            gordoPos = findGordo(frm)
            labelFrame = drawLabel(frm, dedePos[4], dedePos[1], dedePos[0], (0, 0, 255))
            labelFrame = drawLabel(labelFrame, kirbyPos[4], kirbyPos[1], kirbyPos[0], (0, 0, 255))
            hammerPos = findHammer(labelFrame)
            labelFrame = drawLabel(labelFrame, hammerPos[4], hammerPos[1], hammerPos[0], (0, 0, 255))
            labelFrame = drawLabel(labelFrame, gordoPos[4], gordoPos[1], gordoPos[0], (0, 0, 255))
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
                drawPoint(labelFrame, hammerAvg.getSet()[i])
            #dedeFrame = cv2.cvtColor(dedeFrame, cv2.COLOR_BGR2HSV)

            dedeOnPlat = onPlatform(dedePos)
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
                labelFrame = drawAttack(labelFrame)
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
