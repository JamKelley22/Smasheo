import numpy as np

class MovingAvg:
    cursor = 0
    filled = False
    size = 0
    set = []

    def __init__(self, cursor, size):
        self.cursor = cursor
        self.size = size
        self.set = [(0, 0)] * size

    def insert(self, element):
        self.set[self.cursor] = element
        self.cursor += 1
        if (self.cursor >= self.size):
            self.cursor = 0
            self.filled = True

    def getAvg(self):
        subCursor = 0
        sumX = 0
        sumY = 0
        len = 0
        if self.filled:
            len = self.size
        else:
            len = self.cursor
        while subCursor < len:
            sumX += self.set[subCursor][0]
            sumY += self.set[subCursor][1]
            subCursor+=1
        sumX /= len
        sumY /= len
        return (sumX, sumY)

    def getDisplacement(self):
        len = 0
        if self.filled:
            len = self.size
        else:
            len = self.cursor
        list = self.set
        deltaX = list[len-1][0] - list[0][0]
        deltaY = list[len-1][1] - list[0][1]
        return (deltaX, deltaY)

    def area(self):
        poly = self.set
        area = 0.0
        j = len(poly) - 1
        for i in range(0, len(poly)):
            x1 = poly[i][0]
            y1 = poly[i][1]
            x2 = poly[j][0]
            y2 = poly[j][1]
            area += ((x1 + x2) * np.abs(y2 - y1))/2
            j = i
        return area

    def getSet(self):
        return self.set

    def printSet(self):
        print(self.set)
