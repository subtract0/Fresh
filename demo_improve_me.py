#!/usr/bin/env python
"""
Simple demo file for autonomous improvement.
This file intentionally contains obvious improvements for the autonomous system.
"""

def calculate(a, b):
    # This function has no error handling
    result = a / b
    return result

def process_list(items):
    # This could be more efficient
    new_list = []
    for item in items:
        new_list.append(item * 2)
    return new_list

def get_user_name(user_dict):
    # No validation of input
    return user_dict["name"]

# This variable name is not descriptive
x = 42

if __name__ == "__main__":
    print("Demo file ready for autonomous improvement")
