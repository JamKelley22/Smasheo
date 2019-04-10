import Complex

def fft(nums):
    n = len(nums)

    if n == 1:
        return Complex.Complex ([nums[0]])

    evens = [n/2]
