def collatz(n):
    if n <= 1:
        return 1
    else:
        if n % 2 == 0:
            return collatz(n // 2)
        else:
            return collatz(3 * n + 1)

def max_iters():
    return 10

def expected_result_set():
    return [1]
