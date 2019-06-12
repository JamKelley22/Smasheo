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
NUM_BINS = 50


def getFFTMatrix(input, out, mp4, fftsize):
    file_replay = Path(out)

    if file_replay.is_file() == False and mp4 == True:
        command = "ffmpeg -i" + input + "-c copy -map 0:a audio.wav"###
        subprocess.call(command, shell=True)

    audio = wave.open(out, 'rb')
    fmt = {1:'B',2:'h',4:'i'}
    size = fmt[audio.getsampwidth()]
    a = array.array(size)
    a.fromfile(open(out, 'rb'), int(os.path.getsize(out) / a.itemsize))
    bytes = a.tolist()
    audio.close()
    complexNums = list(map(cmplx.Complex, bytes))

    mat = []
    prev = []
    ifft = []

    for i in range(1, len(complexNums)//fftsize):
        start = (i - 1) * fftsize
        stop  = i * fftsize
        mat.append(fft.fft(complexNums[start:stop]))

    return mat

def correlateVectors(mat1, mat2, duration, FFTSize):
    mat2Count = 0
    refMat1 = []
    refMat2 = []
    timeList = []
    refMat1 = []
    for i in range(0, len(mat1)):
        vec1 = list(map(lambda x:np.sqrt(x.real * x.real + x.imag * x.imag), mat2[mat2Count][0:NUM_BINS]))
        vec3 = list(map(lambda x:np.sqrt(x.real * x.real + x.imag * x.imag), mat1[i][0:NUM_BINS]))
        imag = np.correlate(vec1, vec1)
        imag2 = np.correlate(vec1, vec3)
        time = i * (duration/len(mat1))
        delta = np.abs(imag-imag2)
        if (delta <= 1000000000):
            refMat1.append(mat1[i])
            timeList.append(time)
        mat2Count += 1
        if mat2Count == len(mat2):
            mat2Count = 0
    return timeList, refMat1


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
        if numTwos > 1:
            output.append(timeVec[i])
        numTwos = 0
    return output

def compareIntensities(mat1, mat2, timeList, FFTSize):
    matReconstructed = []
    mat2Mag = []
    output = []
    nTimeList = []
    atLeastCount = 0
    if len(mat1[0]) != len(mat2[0]):
        print("Fatal: Bin mismatch")
        return
    mat2FreqIndex = 0
    for i in range(0, len(mat1)):
        for j in range(0, len(mat2)):
            for k in range(0, NUM_BINS):
                cmplx1 = mat1[i][k]
                cmplx2 = mat2[j][k]
                mat1I = fft.getIntensity(cmplx1, FFTSize)
                mat2I = fft.getIntensity(cmplx2, FFTSize)
                if stats.withinPercentage(mat1I, mat2I, 0.01) == True:
                    atLeastCount += 50
                if np.abs(mat2I - mat1I) <= 0.75 and mat2I > 15 and mat1I > 20:
                    atLeastCount += 10
        if (atLeastCount >= 160000):
            output.append(i)
            nTimeList.append(timeList[i])
        atLeastCount = 0
    return output, nTimeList

def removeSimilarTimes(matches, nTimes):
    outputMatches = [matches[0]]
    outputnTimes = [nTimes[0]]
    outputMatches.append(matches[0])
    outputnTimes.append(nTimes[0])
    for i in range(0, len(nTimes)):
        if stats.withinPercentage(nTimes[i-1], nTimes[i], 0.1) == False:
            outputMatches.append(matches[i])
            outputnTimes.append(nTimes[i])
    return outputMatches, outputnTimes

def getAudioDuration(directory):
    audio = wave.open(directory, 'r')
    frames = audio.getnframes()
    rate = audio.getframerate()
    duration = frames/float(rate)
    audio.close()
    return duration*1000

def main():
    fftSize = 256
    print("INFO: Beginning first FFT")
    duration = getAudioDuration("C:/Users/brian/Documents/Smasheo/Audio/games/audio4.wav")
    mat2 = getFFTMatrix("C:/Users/brian/Documents/Smasheo/Audio/King Dedede Sounds/dedeHammerSwing.wav", "C:/Users/brian/Documents/Smasheo/Audio/King Dedede Sounds/dedeHammerSwing.wav", False, fftSize)
    print("INFO: Finished first FFT")
    print("INFO: Started second FFT")
    mat1 = getFFTMatrix("C:/Users/brian/Documents/Smasheo/replays/replay4.mp4", "C:/Users/brian/Documents/Smasheo/Audio/games/audio4.wav", True, fftSize)
    print("INFO: Finished second FFT")
    print("INFO: Started cross-correlation")
    timeList, refMat1 = correlateVectors(mat1, mat2, duration, fftSize)
    print("INFO: Finished cross-correlation")
    print("INFO: Started intensity comparisons")
    matches,nTimes = compareIntensities(refMat1, mat2, timeList, fftSize)
    print("INFO: Finished intensity comparisons")
    print("INFO: finished searching")
    return nTimes
