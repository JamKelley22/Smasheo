import numpy as np

def crossCorrelate(signal1, signal2, delay):

    if len(signal1) != len(signal2):
        return -1

    size = len(signal1)
    avg1real = 0
    avg1imag = 0
    avg2real = 0
    avg2imag = 0

    for i in range(0, size):
        avg1real += signal1[i].real
        avg1imag += signal1[i].imag
        avg2real += signal2[i].real
        avg2imag += signal2[i].imag

    avg1real /= size
    avg1imag /= size
    avg2real /= size
    avg2imag /= size

    avgSqDiff1real = 0
    avgSqDiff1imag = 0
    avgSqDiff2real = 0
    avgSqDiff2imag = 0

    for i in range(0, size):
        avgSqDiff1real += (signal1[i].real - avg1real) * (signal1[i].real - avg1real)
        avgSqDiff1imag += (signal1[i].imag - avg1imag) * (signal1[i].imag - avg1imag)
        avgSqDiff2real += (signal2[i].real - avg2real) * (signal2[i].real - avg2real)
        avgSqDiff2imag += (signal2[i].imag - avg2imag) * (signal2[i].imag - avg2imag)
    denominatorReal = np.sqrt(avgSqDiff1real * avgSqDiff2real)
    denominatorImag = np.sqrt(avgSqDiff1imag * avgSqDiff2imag)

    rReal = 0
    rImag = 0
    for i in range(-delay, delay):
        subReal = 0
        subImag = 0
        for j in range(0, size):
            k = j + i
            #print i, j, k, size
            if k < 0 or k >= size:
                continue
            else:
                subReal += (signal1[j].real - avg1real) * (signal2[j].real - avg2real)
                subImag += (signal1[j].imag - avg1imag) * (signal2[j].imag - avg2imag)
            if k < 0 or k >= size:
                subReal += (signal1[j].real - avg1real) * -avg2real
                subImag += (signal1[j].imag - avg1imag) * -avg2imag
            else:
                 subReal += (signal1[j].real - avg1real) * (signal2[j].real - avg2real)
                 subImag += (signal1[j].imag - avg1imag) * (signal2[j].imag - avg2imag)
            rReal = subReal / denominatorReal
            rImag = subImag / denominatorImag

    return rReal, rImag

def withinPercentage(num1, num2, percent):
    if np.abs(num1 / num2) <= (1-percent):
        return True
    return False

def guessProspects(initStock, stockD, stockK, damageD, damageK):
    if stockD == 0:
        return 100, 0
    if stockK == 0:
        return 0, 100
    dedeChance = 50
    kirbyChance = 50

    if stockD == 0:
        dedeChance = 0
        kirbyChance = 100
        return dedeChance, kirbyChance

    if stockK == 0:
        dedeChance = 100
        kirbyChance = 0
        return dedeChance, kirbyChance

    if stockD < stockK:
        dedeChance -= (stockD / stockK) * 100
        kirbyChance += (stockD / stockK) * 100
    elif stockK > stockD:
        dedeChance += (stockK / stockD) * 100
        kirbyChance -= (stockK / stockD) * 100

    if damageD < damageK:
        dedeChance -= ((damageK - damageD)/5) / stockD
        kirbyChance += ((damageK - damageD)/5) / stockD
    elif damageK > damageD:
        dedeChance += ((damageD - damageK)/5) / stockD
        kirbyChance -= ((damageD - damageK)/5) / stockD

    return kirbyChance, dedeChance
