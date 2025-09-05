#!/usr/bin/env python
"""
Demo file for testing autonomous loop implementation.
Contains real TODOs that should be implementable by the autonomous system.
"""


def calculate_sum(numbers):
    """Calculate the sum of a list of numbers.
    
    Args:
        numbers: List of numeric values to sum
        
    Returns:
        Numeric sum of all values in the list
        
    TODO: Add input validation for empty lists
    """
    return sum(numbers)


def process_user_input(user_input):
    """Process and clean user input string.
    
    Args:
        user_input: Raw input string from user
        
    Returns:
        Cleaned input string with whitespace stripped
        
    TODO: Add input sanitization
    """
    return user_input.strip()


def get_file_size(filename):
    """Get the size of a file in bytes.
    
    Args:
        filename: Path to the file to check
        
    Returns:
        File size in bytes
        
    TODO: Add error handling for missing files
    """
    import os
    return os.path.getsize(filename)


class DataProcessor:
    """Simple data processor for demonstration purposes.
    
    Attributes:
        data: List to store processed data items
    """
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        """Add an item to the data collection.
        
        Args:
            item: Data item to add to the collection
            
        TODO: Add duplicate checking
        """
        self.data.append(item)
    
    def process_all(self):
        """Process all data items in the collection.
        
        TODO: Implement batch processing logic
        """
        pass


if __name__ == "__main__":
    print("Demo file for autonomous loop testing")
