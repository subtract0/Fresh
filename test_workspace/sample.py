def hello_world():
    return "Hello, World!"

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")  # Raise an error if b is 0
    return a / b

# TODO: Add proper error handling
def calculate_area(length, width):
    return length * width