import cv2
import numpy as np
import sys

def getDededeStock(frm):
    newImg = frm[690:710,315:470]
    bw = cv2.cvtColor(newImg, cv2.COLOR_BGR2GRAY)
    dummy, bw = cv2.threshold(bw, 100, 255, cv2.THRESH_BINARY)
    comps, output, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
    stocks = 0
    for i in range(1, len(stats)):
        size = stats[i][4]
        if size >= 135 and size <= 143:
            stocks += 1
        else:
            return -1
    cv2.imshow("Dedede stock", bw)
    return stocks

def getKirbyStock(frm):
    newImg = frm[690:710,810:965]
    bw = cv2.cvtColor(newImg, cv2.COLOR_BGR2GRAY)
    dummy, bw = cv2.threshold(bw, 100, 255, cv2.THRESH_BINARY)
    comps, output, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
    stocks = 0
    for i in range(1, len(stats)):
        size = stats[i][4]
        if size >= 130 and size <= 140:
            stocks += 1
        else:
            return -1
    cv2.imshow("Kirby stock", bw)
    return stocks
