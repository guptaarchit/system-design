"""
Quick Sort Algorithm

Quick Sort is a divide-and-conquer algorithm. It works by selecting a 'pivot' element
from the array and partitioning the other elements into two sub-arrays according to
whether they are less than or greater than the pivot. The sub-arrays are then sorted
recursively.

Time Complexity:
    - Best Case: O(n log n) - when pivot divides array evenly
    - Average Case: O(n log n)
    - Worst Case: O(n²) - when pivot is always smallest or largest element

Space Complexity: O(log n) - recursion stack space

Stable: No (default implementation, can be made stable)

Use Cases:
    - General-purpose sorting
    - When average-case performance matters more than worst-case
    - In-place sorting preferred
    - Cache-efficient due to good locality of reference
"""


def quick_sort(arr, low=0, high=None):
    """
    Sort an array using Quick Sort algorithm.
    
    Args:
        arr: List of comparable elements (will be modified)
        low: Starting index
        high: Ending index
        
    Returns:
        Sorted list
        
    Example:
        >>> quick_sort([10, 7, 8, 9, 1, 5])
        [1, 5, 7, 8, 9, 10]
    """
    if high is None:
        arr = arr.copy()
        high = len(arr) - 1
    elif low == 0 and high == len(arr) - 1:
        arr = arr.copy()
    
    if low < high:
        # pi is partitioning index, arr[pi] is now at right place
        pi = partition(arr, low, high)
        
        # Recursively sort elements before and after partition
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)
    
    return arr


def partition(arr, low, high):
    """
    Partition function using last element as pivot.
    Places pivot at correct position and places all smaller elements
    to left of pivot and all greater elements to right of pivot.
    
    Args:
        arr: Array to partition
        low: Starting index
        high: Ending index
        
    Returns:
        Index of pivot after partitioning
    """
    # Choose the rightmost element as pivot
    pivot = arr[high]
    
    # Index of smaller element (indicates right position of pivot)
    i = low - 1
    
    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    # Place pivot at correct position
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quick_sort_first_pivot(arr, low=0, high=None):
    """
    Quick Sort using first element as pivot.
    
    Args:
        arr: List to sort
        low: Starting index
        high: Ending index
        
    Returns:
        Sorted list
    """
    if high is None:
        arr = arr.copy()
        high = len(arr) - 1
    elif low == 0 and high == len(arr) - 1:
        arr = arr.copy()
    
    if low < high:
        pi = partition_first_pivot(arr, low, high)
        quick_sort_first_pivot(arr, low, pi - 1)
        quick_sort_first_pivot(arr, pi + 1, high)
    
    return arr


def partition_first_pivot(arr, low, high):
    """Partition using first element as pivot."""
    pivot = arr[low]
    i = low + 1
    
    for j in range(low + 1, high + 1):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    
    arr[low], arr[i - 1] = arr[i - 1], arr[low]
    return i - 1


def quick_sort_median_pivot(arr, low=0, high=None):
    """
    Quick Sort using median of three as pivot (better performance).
    
    Args:
        arr: List to sort
        low: Starting index
        high: Ending index
        
    Returns:
        Sorted list
    """
    if high is None:
        arr = arr.copy()
        high = len(arr) - 1
    elif low == 0 and high == len(arr) - 1:
        arr = arr.copy()
    
    if low < high:
        pi = partition_median_pivot(arr, low, high)
        quick_sort_median_pivot(arr, low, pi - 1)
        quick_sort_median_pivot(arr, pi + 1, high)
    
    return arr


def partition_median_pivot(arr, low, high):
    """Partition using median of three as pivot."""
    mid = (low + high) // 2
    
    # Sort low, mid, high and use mid as pivot
    if arr[low] > arr[mid]:
        arr[low], arr[mid] = arr[mid], arr[low]
    if arr[low] > arr[high]:
        arr[low], arr[high] = arr[high], arr[low]
    if arr[mid] > arr[high]:
        arr[mid], arr[high] = arr[high], arr[mid]
    
    # Place median at high position
    arr[mid], arr[high] = arr[high], arr[mid]
    pivot = arr[high]
    
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


def quick_sort_iterative(arr):
    """
    Iterative implementation of Quick Sort using stack.
    
    Args:
        arr: List to sort
        
    Returns:
        Sorted list
    """
    arr = arr.copy()
    n = len(arr)
    
    # Create an auxiliary stack
    stack = [(0, n - 1)]
    
    while stack:
        low, high = stack.pop()
        
        if low < high:
            pi = partition(arr, low, high)
            
            # Push left and right subarrays to stack
            stack.append((low, pi - 1))
            stack.append((pi + 1, high))
    
    return arr


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [10, 7, 8, 9, 1, 5],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Quick Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        sorted_arr = quick_sort(arr)
        print(f"Original: {arr}")
        print(f"Sorted:   {sorted_arr}")
        print()

