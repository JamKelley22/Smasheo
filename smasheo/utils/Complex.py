
class Complex:
    real = 0.0
    imag = 0.0

    def __init__(self,real):
        self.real = realVal
        self.imag = 0.0

    def __init__(self,realVal, imgVal):
        self.real = realVal
        self.imag = imgVal

    def add(self, c):
        real1 = self.real + c.real
        imag1 = self.imag + c.imag
        return Complex(real1, imag1)

    def sub(self, c):
        real1 = self.real - c.real
        imag1 = self.imag - c.imag
        return Complex(real1, imag1)

    def mult(self, c):
        real1 = self.real * c.real - self.imag * c.imag
        imag1 = self.real * c.imag + self.imag * c.real
        return Complex(real1, imag1)

    def scale(scalar):
        return Complex(self.real * scalar, self.imag * scalar)

    def __str__(self):
        return str(self.real) + " " + str(self.imag)
