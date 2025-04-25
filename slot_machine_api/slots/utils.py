"""
Utility functions for the slot machine application.
"""
from typing import List, Sequence, TypeVar, Dict, Any

T = TypeVar('T')


def find_longest_sequence(items: List[int]) -> List[int]:
    """
    Find the longest sequence of consecutive integers in a list.
    
    Args:
        items: List of integers to search
        
    Returns:
        The longest subsequence of consecutive integers
    """
    if not items:
        return []
    
    # Sort the list to ensure we're working with ordered items
    sorted_items = sorted(items)
    
    # Initialize variables for tracking sequences
    current_seq = [sorted_items[0]]
    longest_seq = [sorted_items[0]]
    
    # Find the longest sequence
    for i in range(1, len(sorted_items)):
        if sorted_items[i] == sorted_items[i-1] + 1:
            # Continue the current sequence
            current_seq.append(sorted_items[i])
        else:
            # Start a new sequence
            current_seq = [sorted_items[i]]
        
        # Update longest sequence if current is longer
        if len(current_seq) > len(longest_seq):
            longest_seq = current_seq.copy()
    
    return longest_seq


def transpose_matrix(matrix: List[List[T]]) -> List[List[T]]:
    """
    Transpose a matrix (convert rows to columns and vice versa).
    
    Args:
        matrix: The matrix to transpose
        
    Returns:
        The transposed matrix
    """
    if not matrix or not matrix[0]:
        return []
    
    # Get dimensions
    rows, cols = len(matrix), len(matrix[0])
    
    # Create a new matrix with swapped dimensions
    result = [[None for _ in range(rows)] for _ in range(cols)]
    
    # Fill the transposed matrix
    for i in range(rows):
        for j in range(cols):
            result[j][i] = matrix[i][j]
    
    return result


def get_or_default(dictionary: Dict[Any, T], key: Any, default: T) -> T:
    """
    Get a value from a dictionary or return a default if the key doesn't exist.
    
    Args:
        dictionary: The dictionary to get the value from
        key: The key to look up
        default: The default value to return if the key doesn't exist
        
    Returns:
        The value from the dictionary or the default
    """
    return dictionary.get(key, default)