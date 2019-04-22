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
MIN_MATCHES = 1500
NUM_BINS = 50

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

    print len(complexNums)
    print "Samples: " + str(len(bytes))
    mat = []
    prev = []
    ifft = []
    print len(mat)
    # for i in range(0, len(complexNums)):
    #     multiplier = 0.5 * (1 - np.cos(2 * np.pi * i / (fftsize - 1)))
    #     complexNums[i] = complexNums[i].scale(multiplier)
    for i in range(1, len(complexNums)/fftsize):
        start = (i - 1) * fftsize
        stop  = i * fftsize
        mat.append(fft.fft(complexNums[start:stop]))
        #prev.append(complexNums[start:stop])

    # if mp4 == False:
    #     fft.matrixToCSV(prev, "./dedede512.csv")
    return mat

def correlateMatches(mat1, mat2, duration, matches, FFTSize):
    timeSampleRatio = duration / len(mat1)
    size = len(mat2)
    refMat = []
    output = []

    for i in range(0, len(mat2)):
        temp = []
        for j in range(0, NUM_BINS):
            r = stats.crossCorrelate(mat2[i], mat2[i], j)
            temp.append(np.sqrt(r[0] * r[0] + r[1] * r[1]))
        refMat.append(temp)

    for i in range(0, len(matches)):
        start = matches[i]
        for j in range(0, size):
            numTwos = 0
            for k in range(0, NUM_BINS):
                r = stats.crossCorrelate(mat1[start + j][0:NUM_BINS], mat2[j][0:NUM_BINS], k)
                rMag = np.sqrt(r[0] * r[0] + r[1] * r[1])
                if refMat[j][k] - rMag <= 0.5:
                    numTwos += 1
        print start * timeSampleRatio, numTwos
        output.append(start)
        numTwos = 0
    return output


def getAllMatches2(mat1, mat2, FFTSize):
    matReconstructed = []
    mat2Mag = []
    output = []
    atLeastCount = 0
    if len(mat1) < len(mat2) :
        print "size mismatch"
        return
    if len(mat1[0]) != len(mat2[0]):
        print "Bin mismatch"
        return
    mat2FreqIndex = 0
    for i in range (0, len(mat1)):
        for j in range (0, NUM_BINS):
            curReconValue = 0
            mat2Mag = np.sqrt(mat2[mat2FreqIndex][j].real * mat2[mat2FreqIndex][j].real + mat2[mat2FreqIndex][j].imag * mat2[mat2FreqIndex][j].imag)
            mat1Mag = np.sqrt(mat1[i][j].real * mat1[i][j].real + mat1[i][j].imag * mat1[i][j].imag)
            if (mat1Mag <= mat2Mag and (np.abs(mat1Mag) >= 1000 and np.abs(mat2Mag) >= 1000)):
                atLeastCount += 1
        mat2FreqIndex += 1
        if mat2FreqIndex == len(mat2):
            mat2FreqIndex = 0
            if (atLeastCount >= MIN_MATCHES):
                output.append(i)
                print i, atLeastCount

            atLeastCount = 0
            mat2FreqIndex = 0

    return output

def getAllMatches(mat1, mat2, duration, FFTSize):
    timeSampleRatio = duration / len(mat1)
    output = []
    if len(mat1) < len(mat2):
        print("The first matrix needs to be bigger than the second")
        return
    if len(mat1[0]) != len(mat2[0]):
        print "Frequency bin size mismatch"
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
                print numCloseMatches, time, (avgReal/avgImag), magSum, avgMag, sumPhase, avgPhase, avgReal, avgImag
                output.append(i * timeSampleRatio)
                print ccMag, ccMag * numCloseMatches
                print ccMagAvg/len(mat2), ccSelfMag, "dI", ccMag, ccSelfMag, ccSelfMagAvg

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
    mat2 = getFFTMatrix("./dededehit.wav", "../Audio/King Dedede Sounds/dededehit.wav", False, fftSize)
    print len(mat2)
    mat1 = getFFTMatrix("../replays/replay1.mp4", "./audio.wav", True, fftSize)
    # #fft.matrixToCSV(mat1, "./replay1FFT256.csv")
    # mat3 = mat2
    # for i in range (0, len(mat2)/2):
    #     for j in range(0, len(mat2)/2):
    #         cc = stats.crossCorrelate(mat2[i], mat3[i], j)
    #         ccSelf = stats.crossCorrelate(mat2[i], mat2[i], j)
    #         ccMag = np.sqrt(cc[0] * cc[0] + cc[1] * cc[1])
    #         ccSelfMag = np.sqrt(ccSelf[0] * ccSelf[0] + ccSelf[1] * ccSelf[1])
    #         print np.sqrt(cc[0] * cc[0] + cc[1] * cc[1]), ccSelf, cc, ccMag, ccSelfMag, ccSelfMag - ccMag, i, j
    #fft.matrixToCSV(mat2, "./dededeFFT512")

    print "finished FFT"
    print duration
    matches = getAllMatches2(mat1, mat2, fftSize)
    times = correlateMatches(mat1, mat2, duration, matches, fftSize)
    print "finished searching"

    return times

#main()
