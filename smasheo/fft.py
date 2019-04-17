import Complex as cmplx
import numpy as np

def fft(vec):
    N = len(vec)

    if N == 1:
        return [vec[0]]

    evens = []
    odds = []
    output = [0]*N

    fftEvens = fft(vec[::2])
    fftOdds = fft(vec[1::2])
    for k in range(0, N/2):
        exp = cmplx.Complex(np.cos(-2 * np.pi * k / N), np.sin(-2 * np.pi * k / N))
        product = exp.mult(fftOdds[k])
        output[k] = fftEvens[k].add(product)
        output[k + N / 2] = fftEvens[k].sub(product)

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

def matrixToCSV(mat, outputDir):
    f = open(outputDir, 'w')
    for i in range(0, len(mat)):
        for j in range(0, len(mat[i])):
            f.write(str(mat[i][j]) + ", ")
        f.write("\n")
