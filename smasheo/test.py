import numpy as np
import sys
import Complex as cmplx
import fft
import wave
import subprocess
from pathlib import Path
import struct
import array
import os
import fft
import stats

MAX_DIFF = 10
MIN_MATCHES = 100
NUM_BINS = 75

def getFFTMatrix(input, out, mp4, fftsize):
    file_replay = Path(out)

    if file_replay.is_file() == False and mp4 == True:
        command = "ffmpeg -i" + input + "-c copy -map 0:a audio.wav"
        subprocess.call(command, shell=True)

    audio = wave.open(out, 'rb')
    fmt = {1:'B',2:'h',4:'i'}
    size = fmt[audio.getsampwidth()]
    a = array.array(size)
    a.fromfile(open(out, 'rb'), os.path.getsize(out)/a.itemsize)
    bytes = a.tolist()
    audio.close()
    complexNums = map(cmplx.Complex, bytes)

    print(len(complexNums))
    print("Samples: " + str(len(bytes)))
    mat = []
    prev = []
    ifft = []
    print(len(mat))
    # for i in range(0, len(complexNums)):
    #     multiplier = 0.5 * (1 - np.cos(2 * np.pi * i / (fftsize - 1)))
    #     complexNums[i] = complexNums)[i].scale(multiplier)
    for i in range(1, len(complexNums)/fftsize):
        start = (i - 1) * fftsize
        stop  = i * fftsize
        mat.append(fft.fft(complexNums[start:stop]))
        #prev.append(complexNums[start:stop])

    # if mp4 == False:
    #     fft.matrixToCSV(prev, "./dedede512.csv")
    return mat

#def correlateVectors(mat1, mat2, duration, FFTSize):


def correlateMatches(mat1, mat2, duration, timeVec, matches, FFTSize):
    timeSampleRatio = duration / len(mat1)
    size = len(mat2)
    refMat = []
    output = []
    outTime = []

    for i in range(0, len(mat2)):
        temp = []
        for j in range(0, NUM_BINS):
            r = stats.crossCorrelate(mat2[i], mat2[i], j)
            temp.append(np.sqrt(r[0] * r[0] + r[1] * r[1]))
        refMat.append(temp)

    for i in range(0, len(matches)):
        for j in range(0, size):
            numTwos = 0
            for k in range(0, NUM_BINS):
                r = stats.crossCorrelate(mat1[matches[i]][0:NUM_BINS], mat2[j][0:NUM_BINS], k)
                rMag = np.sqrt(r[0] * r[0] + r[1] * r[1])
                if np.abs(refMat[j][k] - rMag) <= 1.5:
                    numTwos += 1
                # if k >= 5 and numTwos < 5:
                #     break
        if numTwos > 1:
            print(timeVec[i], numTwos)
            output.append(timeVec[i])
        numTwos = 0
    return output


def getAllMatches2(mat1, mat2, timeList, FFTSize):
    matReconstructed = []
    mat2Mag = []
    output = []
    nTimeList = []
    atLeastCount = 0
    if len(mat1) < len(mat2) :
        print("size mismatch")
        return
    if len(mat1[0]) != len(mat2[0]):
        print("Bin mismatch")
        return
    mat2FreqIndex = 0
    #For every vector in mat1, compare it to every vector in mat2
    for i in range(0, len(mat1)):
        for j in range(0, len(mat2)):
            for k in range(0, NUM_BINS):
                cmplx1 = mat1[i][k]
                cmplx2 = mat2[j][k]
                mat1Mag = np.sqrt(cmplx1.real * cmplx1.real + cmplx1.imag * cmplx1.imag)
                mat2Mag = np.sqrt(cmplx2.real * cmplx2.real + cmplx2.imag * cmplx2.imag)
                if mat1Mag <= mat2Mag:
                    atLeastCount += 1
        if (atLeastCount >= 1000 and atLeastCount <= 3000 ):
            output.append(i)
            nTimeList.append(timeList[i])
            print(timeList[i], i, atLeastCount)
        atLeastCount = 0
    return output, nTimeList

def getAllMatches(mat1, mat2, duration, FFTSize):
    timeSampleRatio = duration / len(mat1)
    output = []
    if len(mat1) < len(mat2):
        print("The first matrix needs to be bigger than the second")
        return
    if len(mat1[0]) != len(mat2[0]):
        print("Frequency bin size mismatch")
    numCloseMatches = 0
    mat2FreqIndex = 0
    avgPhase = 0
    avgReal = 0
    avgImag = 0
    avgMag = 0
    ccMagAvg = 0
    ccSelfMagAvg = 0
    avgDelta = 0
    for i in range(0, len(mat1)):

        for j in range(0, NUM_BINS):
            cc = stats.crossCorrelate(mat1[i][0:NUM_BINS], mat2[mat2FreqIndex][0:NUM_BINS], j)
            ccMag = np.sqrt(cc[0] * cc[0] + cc[1] * cc[1])
            ccSelf = stats.crossCorrelate(mat2[mat2FreqIndex][0:NUM_BINS], mat2[mat2FreqIndex][0:NUM_BINS], j)
            ccSelfMag = np.sqrt(ccSelf[0] * ccSelf[0] + ccSelf[1] * ccSelf[1]) - ccMag
            ccSelfMagAvg += ccSelfMag
            ccMagAvg += ccMag
            delta = mat2[mat2FreqIndex][j].sub(mat1[i][j])
            intensity1 = fft.getIntensity(mat1[i][j], j)
            intensity2 = fft.getIntensity(mat2[mat2FreqIndex][j], j)
            deltaIntensity = intensity2 - intensity1
            avgPhase += delta.getPhase()
            avgReal += delta.real
            avgImag += delta.imag

            if ccSelfMag <= 0.5:#(abs(deltaIntensity) <= MAX_DIFF):
                numCloseMatches += 1
            magnitude = np.sqrt(delta.real * delta.real + delta.imag * delta.imag)
            avgMag += magnitude
        mat2FreqIndex += 1
        if mat2FreqIndex == len(mat2):
            mat2FreqIndex = 0
            bins = len(mat2[0])
            samples = len(mat2)
            n = bins * samples
            if (numCloseMatches >= MIN_MATCHES):
                sumPhase = avgPhase
                magSum = avgMag
                avgMag /= len(mat2) * NUM_BINS
                avgPhase /= len(mat2) * NUM_BINS
                avgReal /= len(mat2) * NUM_BINS
                avgImag /= len(mat2) * NUM_BINS
                ccMagAvg/= len(mat2) * NUM_BINS
                ccSelfMagAvg /= len(mat2)
                time = i * timeSampleRatio
                print(numCloseMatches, time, (avgReal/avgImag), magSum, avgMag, sumPhase, avgPhase, avgReal, avgImag)
                output.append(i * timeSampleRatio)
                print(ccMag, ccMag * numCloseMatches)
                print(ccMagAvg/len(mat2), ccSelfMag, "dI", ccMag, ccSelfMag, ccSelfMagAvg)

            correlationVec = []
            ccMagAvg = 0
            avgPhase = 0
            avgMag = 0
            avgReal = 0
            avgImag = 0
            ccSelfMagAvg = 0
                #print str(i) + ": " + str(numCloseMatches) + " / " + str(len(mat2) * 1024)
            numCloseMatches = 0
    return output

def getAudioDuration(directory):
    audio = wave.open(directory, 'r')
    frames = audio.getnframes()
    rate = audio.getframerate()
    duration = frames/float(rate)
    audio.close()
    return duration*1000

def main():
    fftSize = 256
    duration = getAudioDuration("./audio.wav")
    mat2 = getFFTMatrix("./dededehit.wav", "../Audio/King Dedede Sounds/dedeUpSmash2.wav", False, fftSize)
    #print len(mat2)
    mat1 = getFFTMatrix("../replays/replay1.mp4", "./audio.wav", True, fftSize)
    # #fft.matrixToCSV(mat1, "./replay1FFT256.csv")
    mat3 = mat2
    mat2Count = 0
    refMat1 = []
    refMat2 = []
    timeList = []
    for i in range(0, len(mat1)):
        vec1 = map(lambda x:np.sqrt(x.real * x.real + x.imag * x.imag), mat2[mat2Count][0:NUM_BINS])
        vec3 = map(lambda x:np.sqrt(x.real * x.real + x.imag * x.imag), mat1[i][0:NUM_BINS])
        imag = np.correlate(vec1, vec1)
        imag2 = np.correlate(vec1, vec3)
        time = i * (duration/len(mat1))
        delta = np.abs(imag-imag2)
        if (delta <= 150000000):
            refMat1.append(mat1[i])
            timeList.append(time)
            print(time, imag, imag2, delta)
        mat2Count += 1
        if mat2Count == len(mat2):
            mat2Count = 0

    print("finished FFT")
    print(duration)
    matches,nTimes = getAllMatches2(refMat1, mat2, timeList, fftSize)
    print(matches)
    print("finished searching")

    return nTimes

#main()
