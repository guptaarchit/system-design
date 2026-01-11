"""
Radix Sort Algorithm

Radix Sort is a non-comparative sorting algorithm. It avoids comparison by creating
and distributing elements into buckets according to their radix. For elements with
more than one significant digit, this bucketing process is repeated for each digit,
while preserving the ordering of the prior step, until all digits have been considered.

Radix Sort uses Counting Sort as a subroutine to sort.

Time Complexity: O(d * (n + k)) where:
    - d = number of digits
    - n = number of elements
    - k = range of digits (usually 10 for decimal)
    
    - Best Case: O(d * (n + k))
    - Average Case: O(d * (n + k))
    - Worst Case: O(d * (n + k))

Space Complexity: O(n + k)

Stable: Yes

Use Cases:
    - Sorting integers with fixed number of digits
    - Sorting strings lexicographically
    - When range of values is known
    - Sorting by multiple keys
"""


def radix_sort(arr):
    """
    Sort an array using Radix Sort algorithm.
    Assumes non-negative integers.
    
    Args:
        arr: List of non-negative integers
        
    Returns:
        Sorted list
        
    Example:
        >>> radix_sort([170, 45, 75, 90, 802, 24, 2, 66])
        [2, 24, 45, 66, 75, 90, 170, 802]
    """
    if not arr:
        return []
    
    arr = arr.copy()
    
    # Find the maximum number to know number of digits
    max_num = max(arr)
    
    # Do counting sort for every digit. Note that instead
    # of passing digit number, exp is passed. exp is 10^i
    # where i is current digit number
    exp = 1
    while max_num // exp > 0:
        counting_sort_by_digit(arr, exp)
        exp *= 10
    
    return arr


def counting_sort_by_digit(arr, exp):
    """
    A function to do counting sort of arr[] according to
    the digit represented by exp.
    
    Args:
        arr: Array to sort
        exp: Current digit position (1, 10, 100, ...)
    """
    n = len(arr)
    output = [0] * n  # Output array
    count = [0] * 10  # Count array for digits 0-9
    
    # Store count of occurrences in count[]
    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1
    
    # Change count[i] so that count[i] now contains actual
    # position of this digit in output[]
    for i in range(1, 10):
        count[i] += count[i - 1]
    
    # Build the output array
    for i in range(n - 1, -1, -1):
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
    
    # Copy the output array to arr[], so that arr[] now
    # contains sorted numbers according to current digit
    for i in range(n):
        arr[i] = output[i]


def radix_sort_strings(arr):
    """
    Radix Sort for strings (lexicographic sorting).
    
    Args:
        arr: List of strings
        
    Returns:
        Sorted list of strings
    """
    if not arr:
        return []
    
    arr = arr.copy()
    
    # Find maximum length
    max_len = max(len(s) for s in arr) if arr else 0
    
    # Pad strings to same length
    padded = [s.ljust(max_len) for s in arr]
    
    # Sort from least significant character to most significant
    for pos in range(max_len - 1, -1, -1):
        counting_sort_by_char(padded, pos)
    
    # Remove padding
    return [s.rstrip() for s in padded]


def counting_sort_by_char(arr, pos):
    """
    Counting sort for strings by character at given position.
    
    Args:
        arr: Array of strings
        pos: Character position to sort by
    """
    n = len(arr)
    output = [None] * n
    count = [0] * 256  # ASCII range
    
    # Count occurrences
    for s in arr:
        char_val = ord(s[pos]) if pos < len(s) else 0
        count[char_val] += 1
    
    # Cumulative count
    for i in range(1, 256):
        count[i] += count[i - 1]
    
    # Build output
    for i in range(n - 1, -1, -1):
        char_val = ord(arr[i][pos]) if pos < len(arr[i]) else 0
        output[count[char_val] - 1] = arr[i]
        count[char_val] -= 1
    
    # Copy back
    for i in range(n):
        arr[i] = output[i]


def radix_sort_negative(arr):
    """
    Radix Sort that handles negative numbers.
    
    Args:
        arr: List of integers (can include negatives)
        
    Returns:
        Sorted list
    """
    if not arr:
        return []
    
    # Separate positive and negative numbers
    negatives = [-x for x in arr if x < 0]
    positives = [x for x in arr if x >= 0]
    
    # Sort both separately
    sorted_negatives = radix_sort(negatives)
    sorted_positives = radix_sort(positives)
    
    # Reverse negatives and negate back, then combine
    sorted_negatives = [-x for x in reversed(sorted_negatives)]
    
    return sorted_negatives + sorted_positives


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [170, 45, 75, 90, 802, 24, 2, 66],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Radix Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        if arr and all(isinstance(x, int) and x >= 0 for x in arr):
            sorted_arr = radix_sort(arr)
            print(f"Original: {arr}")
            print(f"Sorted:   {sorted_arr}")
            print()
    
    # String sorting example
    print("\nRadix Sort for Strings:")
    print("=" * 50)
    strings = ["word", "category", "cat", "new", "news", "world", "bear", "at", "work", "time"]
    sorted_strings = radix_sort_strings(strings)
    print(f"Original: {strings}")
    print(f"Sorted:   {sorted_strings}")

