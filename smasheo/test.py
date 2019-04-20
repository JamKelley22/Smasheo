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
MIN_MATCHES = 7000
NUM_BINS = 128

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
    for i in range(0, len(mat1)):
        cc = stats.crossCorrelate(mat1[i], mat2[mat2FreqIndex], FFTSize)
        ccMag = np.sqrt(cc[0] * cc[0] + cc[1] * cc[1])
        for j in range(0, NUM_BINS):
            delta = mat2[mat2FreqIndex][j].sub(mat1[i][j])
            intensity1 = fft.getIntensity(mat1[i][j], j)
            intensity2 = fft.getIntensity(mat2[mat2FreqIndex][j], j)
            deltaIntensity = intensity2 - intensity1

            if (abs(deltaIntensity) <= MAX_DIFF):
                avgPhase += delta.getPhase()
                avgReal += delta.real
                avgImag += delta.imag
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
                avgMag /= numCloseMatches
                avgPhase /= numCloseMatches
                avgReal /= numCloseMatches
                avgImag /= numCloseMatches
                time = i * timeSampleRatio
                print numCloseMatches, time, (avgReal/avgImag), magSum, avgMag, sumPhase, avgPhase, avgReal, avgImag
                output.append(i * timeSampleRatio)
                print cc
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
    mat1 = getFFTMatrix("../replays/replay1.mp4", "./audio.wav", True, fftSize)
    fft.matrixToCSV(mat1, "./replay1FFT256.csv")
    mat2 = getFFTMatrix("./dededehit.wav", "../Audio/King Dedede Sounds/dedeUpSmash3.wav", False, fftSize)
    #mat3 = mat2
    # for i in range (0, len(mat2)):
    #     cc = stats.crossCorrelate(mat2[i], mat3[i], 256)
    #     print np.sqrt(cc[0] * cc[0] + cc[1] * cc[1])
    #fft.matrixToCSV(mat2, "./dededeFFT512")

    print "finished FFT"
    print duration
    times = getAllMatches(mat1, mat2, duration, 512)
    print "finished searching"

    return times

#main()
