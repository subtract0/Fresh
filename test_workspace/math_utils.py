def calculate_square(n):
    return n * n

# Updated factorial function with input validation
def factorial(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return 1
    return n * factorial(n - 1)