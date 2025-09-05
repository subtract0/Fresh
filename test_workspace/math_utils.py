def calculate_square(n):
    """
    Calculate the square of a given number.

    Parameters:
    n (int or float): The number to be squared.

    Returns:
    int or float: The square of the input number.
    """
    return n * n

# Updated factorial function with input validation
def factorial(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    if n == 0:
        return 1
    return n * factorial(n - 1)

# Simple function to print a hello world message
def hello_world():
    """Prints 'Hello, World!' to the console."""
    print("Hello, World!")