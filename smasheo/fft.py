import Complex as cmplx
import numpy as np

max16bit = 32768

def fft(vec):
    N = len(vec)
    if N == 1:
        return [vec[0]]
    evens = []
    odds = []
    output = [0]*N
    fftEvens = fft(vec[::2])
    fftOdds = fft(vec[1::2])
    for k in range(0, N // 2):
        exp = cmplx.Complex(np.cos(-2 * np.pi * k / N), np.sin(-2 * np.pi * k / N))
        product = exp.mult(fftOdds[k])
        output[k] = fftEvens[k].add(product)
        output[k + N // 2] = fftEvens[k].sub(product)
    return output

def ifft(vec):
    N = len(vec)

    if N == 1:
        return [vec[0]]

    evens = []
    odds = []
    output = [0]*N
    for k in range(0, N/2):
        evens.append(vec[2 * k])
        odds.append(vec[2 * k + 1])

    fftEvens = fft(evens)
    fftOdds = fft(odds)
    for k in range(0, N/2):
        exp = cmplx.Complex(np.cos(-2 * np.pi * k / N), np.sin(-2 * np.pi * k / N))
        product = exp.mult(fftOdds[k])
        product = product.scale(float(1)/float(N))
        output[k] = fftEvens[k].sub(product)
        output[k + N / 2] = fftEvens[k].add(product)
    return output

def getIntensity(complex, FFTSize):
    real = complex.real
    imag = complex.imag
    magnitude = np.sqrt(real * real + imag * imag)
    intensity = -20 * np.log10(magnitude/max16bit)
    return intensity

def matrixToCSV(mat, outputDir):
    f = open(outputDir+".csv", 'w')
    mag = open(outputDir + "mag.csv", 'w')
    db = open(outputDir + "db.csv", "w")
    for i in range(0, len(mat)):
        for j in range(0, len(mat[i])):
            f.write(str(mat[i][j]) + ", ")
            real = mat[i][j].real
            imag = mat[i][j].imag
            magnitude = np.sqrt(real * real + imag * imag)
            intensity = getIntensity(mat[i][j], 256)
            mag.write(str(magnitude) + ", ")
            db.write(str(intensity) +  ", ")
        f.write("\n")
        mag.write("\n")
        db.write("\n")
