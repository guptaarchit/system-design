"""
Counting Sort Algorithm

Counting Sort is a sorting technique based on keys between a specific range.
It works by counting the number of objects having distinct key values (kind of hashing).
Then doing some arithmetic to calculate the position of each object in the output sequence.

Counting sort is efficient if the range of input data is not significantly greater than
the number of objects to be sorted. Consider the situation where the input sequence is
between range 1 to 10K and the data is 10, 5, 10K, 5K.

Time Complexity: O(n + k) where n is the number of elements and k is the range
    - Best Case: O(n + k)
    - Average Case: O(n + k)
    - Worst Case: O(n + k)

Space Complexity: O(k) - where k is the range of input

Stable: Yes

Use Cases:
    - When range of input values is not significantly larger than number of elements
    - Integer sorting
    - As a subroutine in Radix Sort
    - When there are many repeated values
"""


def counting_sort(arr):
    """
    Sort an array using Counting Sort algorithm.
    Assumes non-negative integers.
    
    Args:
        arr: List of non-negative integers
        
    Returns:
        Sorted list
        
    Example:
        >>> counting_sort([4, 2, 2, 8, 3, 3, 1])
        [1, 2, 2, 3, 3, 4, 8]
    """
    if not arr:
        return []
    
    # Find the maximum value in array
    max_val = max(arr)
    min_val = min(arr)
    
    # Create count array
    range_size = max_val - min_val + 1
    count = [0] * range_size
    
    # Store count of each element
    for num in arr:
        count[num - min_val] += 1
    
    # Modify count array to store cumulative count
    for i in range(1, range_size):
        count[i] += count[i - 1]
    
    # Build output array
    output = [0] * len(arr)
    
    # Build output array in reverse order for stability
    for i in range(len(arr) - 1, -1, -1):
        output[count[arr[i] - min_val] - 1] = arr[i]
        count[arr[i] - min_val] -= 1
    
    return output


def counting_sort_simple(arr):
    """
    Simplified version of counting sort (not stable).
    
    Args:
        arr: List of non-negative integers
        
    Returns:
        Sorted list
    """
    if not arr:
        return []
    
    max_val = max(arr)
    min_val = min(arr)
    
    # Create count array
    count = [0] * (max_val - min_val + 1)
    
    # Count occurrences
    for num in arr:
        count[num - min_val] += 1
    
    # Build output array
    output = []
    for i, freq in enumerate(count):
        output.extend([i + min_val] * freq)
    
    return output


def counting_sort_general(arr, key_func=None):
    """
    General counting sort that can handle any comparable elements
    by using a key function.
    
    Args:
        arr: List of elements
        key_func: Function to extract integer key from element
        
    Returns:
        Sorted list
    """
    if not arr:
        return []
    
    if key_func is None:
        key_func = lambda x: x
    
    # Extract keys
    keys = [key_func(x) for x in arr]
    max_key = max(keys)
    min_key = min(keys)
    
    # Create count array
    count = [0] * (max_key - min_key + 1)
    
    # Count occurrences
    for key in keys:
        count[key - min_key] += 1
    
    # Modify count for cumulative positions
    for i in range(1, len(count)):
        count[i] += count[i - 1]
    
    # Build output array
    output = [None] * len(arr)
    
    # Process in reverse for stability
    for i in range(len(arr) - 1, -1, -1):
        pos = count[keys[i] - min_key] - 1
        output[pos] = arr[i]
        count[keys[i] - min_key] -= 1
    
    return output


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [4, 2, 2, 8, 3, 3, 1],
        [1, 4, 1, 2, 7, 5, 2],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Counting Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        if arr and all(isinstance(x, int) and x >= 0 for x in arr):
            sorted_arr = counting_sort(arr)
            print(f"Original: {arr}")
            print(f"Sorted:   {sorted_arr}")
            print()

