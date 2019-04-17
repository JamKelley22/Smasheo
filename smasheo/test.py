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
    for i in range(1, len(complexNums)/fftsize):
        start = (i - 1) * fftsize
        stop  = i * fftsize
        mat.append(fft.fft(complexNums[start:stop]))
        prev.append(complexNums[start:stop])

    if mp4 == False:
        fft.matrixToCSV(prev, "./dedede512.csv")
    return mat

def getAllMatches(mat1, mat2, duration):
    timeSampleRatio = duration / len(mat1)
    output = []
    if len(mat1) < len(mat2):
        print("The first matrix needs to be bigger")
        return
    if len(mat1[0]) != len(mat2[0]):
        print "Frequency bin size mismatch"
    numCloseMatches = 0
    mat2FreqIndex = 0
    for i in range(0, len(mat1)):
        for j in range(0, len(mat2)):
            delta = mat2[mat2FreqIndex][j].sub(mat1[i][j])
            mat1Real = mat1[i][j].real
            mat1Imag = mat1[i][j].imag
            deltaReal = delta.real
            deltaImag = delta.imag
            deltaMagnitude = np.sqrt(deltaReal * deltaReal + deltaImag * deltaImag)
            if (abs(deltaMagnitude) <= 10):
                numCloseMatches += 1
        mat2FreqIndex += 1
        print numCloseMatches
        if mat2FreqIndex == len(mat2):
            mat2FreqIndex = 0
            bins = len(mat2[0])
            samples = len(mat2)
            n = bins * samples
            if (numCloseMatches >=10):
                output.append(i * timeSampleRatio)
                print i * timeSampleRatio
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
    duration = getAudioDuration("./audio.wav")
    mat1 = getFFTMatrix("../replays/replay1.mp4", "./audio.wav", True, 512)
    #fft.matrixToCSV(mat1, "./replay1FFT256.csv")
    mat2 = getFFTMatrix("./dededehit.wav", "./dededehit.wav", False, 512)
    fft.matrixToCSV(mat2, "./dededeFFT256.csv")

    print "finished FFT"
    print duration
    times = getAllMatches(mat1, mat2, duration)
    print "finished searching"

    return times

#main()
