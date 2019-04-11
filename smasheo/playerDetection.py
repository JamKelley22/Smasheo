import cv2
import numpy as np
import sys
sys.path.insert(0, '../utils')
import Complex
import fft
sys.path.insert(0, '../')
import test

# Orange: R: 255 G: 141 B: 0
# Red: R 237 G: 0 B: 1
dedePos = [];

def drawNameDedede(bw, frm):
    comps, output, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)

    if len(stats) > 1:
        biggest = stats[1]
        for i in range(1, comps):
            if stats[i][4] > biggest[4]:
                biggest = stats[i]
        cv2.putText(frm, "King Dedede",(biggest[0], biggest[1]),cv2.FONT_HERSHEY_SIMPLEX, 1, (255,100,100), 2, cv2.LINE_AA)
    return frm

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
    return drawNameDedede(mask, frm);

clips = ['../replays/replay3.mp4']
for i in range(len(clips)):
    upSmashes = test.main()
    vid = cv2.VideoCapture(clips[i])
    width = int(vid.get(3))
    height = int(vid.get(4))
    fourcc = cv2.VideoWriter_fourcc('H','2','6','4')
    title = "output" + str(i) + ".mp4"
    writer = cv2.VideoWriter(title, fourcc,60.0,(width, height))
    count = 0
    while(vid.isOpened()):
        val, frm = vid.read()
        if val == True:
            bw = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
            dummy, bw = cv2.threshold(bw, 100, 255, cv2.THRESH_BINARY)
            dedeFrame = findDedede(frm)
            if (count > 2000):
                cv2.imshow('video ', dedeFrame)
            print count
            count += 1
            writer.write(frm)
            if (cv2.waitKey(25) & 0xFF == ord('q')):
                break
        else:
            break;
    vid.release()
    writer.release()
    cv2.destroyAllWindows()
