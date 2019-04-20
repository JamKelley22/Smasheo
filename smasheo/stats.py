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
        avg2real += signal1[i].real
        avg2imag += signal1[i].imag

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
        avgSqDiff1imag += (signal1[i].imag - avg1real) * (signal1[i].imag - avg1real)
        avgSqDiff2real += (signal1[i].real - avg1real) * (signal1[i].real - avg1real)
        avgSqDiff2imag += (signal1[i].imag - avg1real) * (signal1[i].imag - avg1real)
    denominatorReal = np.sqrt(avgSqDiff1real * avgSqDiff2real)
    denominatorImag = np.sqrt(avgSqDiff1imag * avgSqDiff2imag)

    rReal = 0
    rImag = 0
    for i in range(delay * -1, delay):
        subReal = 0
        subImag = 0
        for j in range(0, size):
            k = j + delay
            #print i, j, k, size
            if k < 0 or k >= size:
                continue
            else:
                subReal += (signal1[j].real - avg1real) * (signal2[k].real - avg2real)
                subImag += (signal1[j].imag - avg1imag) * (signal2[k].imag - avg2imag)
            if k < 0 or k >= size:
                subReal += (signal1[j].real - avg1real) * -avg2real
                subImag += (signal1[j].imag - avg1imag) * -avg2imag
            else:
                 subReal += (signal1[j].real - avg1real) * (signal2[k].real - avg2real)
                 subImag += (signal1[j].imag - avg1imag) * (signal2[k].imag - avg2imag)
            rReal = subReal / denominatorReal
            rImag = subImag / denominatorImag

    return rReal, rImag
