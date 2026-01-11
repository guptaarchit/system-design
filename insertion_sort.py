"""
Insertion Sort Algorithm

Insertion Sort is a simple sorting algorithm that builds the final sorted array
one item at a time. It is much less efficient on large lists than more advanced
algorithms such as quicksort, heapsort, or merge sort.

However, insertion sort provides several advantages:
- Simple implementation
- Efficient for small data sets
- More efficient in practice than other O(n²) algorithms
- Adaptive: efficient for data sets that are already substantially sorted
- Stable: does not change the relative order of elements with equal keys
- In-place: only requires a constant amount O(1) of additional memory space

Time Complexity:
    - Best Case: O(n) - when array is already sorted
    - Average Case: O(n²)
    - Worst Case: O(n²) - when array is reverse sorted

Space Complexity: O(1) - in-place sorting

Stable: Yes

Use Cases:
    - Small datasets
    - Nearly sorted data
    - Hybrid algorithms (e.g., Timsort uses insertion sort for small subarrays)
"""


def insertion_sort(arr):
    """
    Sort an array using Insertion Sort algorithm.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
        
    Example:
        >>> insertion_sort([12, 11, 13, 5, 6])
        [5, 6, 11, 12, 13]
    """
    arr = arr.copy()  # Don't modify original array
    
    # Traverse through 1 to len(arr)
    for i in range(1, len(arr)):
        key = arr[i]  # Current element to be inserted
        
        # Move elements of arr[0..i-1], that are greater than key,
        # to one position ahead of their current position
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        
        arr[j + 1] = key
    
    return arr


def insertion_sort_recursive(arr, n=None):
    """
    Recursive implementation of Insertion Sort.
    
    Args:
        arr: List of comparable elements
        n: Number of elements to sort (optional, defaults to len(arr))
        
    Returns:
        Sorted list
    """
    if n is None:
        n = len(arr)
    
    # Base case
    if n <= 1:
        return arr
    
    # Sort first n-1 elements
    insertion_sort_recursive(arr, n - 1)
    
    # Insert last element at its correct position in sorted array
    last = arr[n - 1]
    j = n - 2
    
    while j >= 0 and arr[j] > last:
        arr[j + 1] = arr[j]
        j -= 1
    
    arr[j + 1] = last
    return arr


def binary_insertion_sort(arr):
    """
    Binary Insertion Sort - uses binary search to find the insertion position.
    Reduces number of comparisons but not swaps.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
    """
    arr = arr.copy()
    
    for i in range(1, len(arr)):
        key = arr[i]
        
        # Find position to insert using binary search
        left, right = 0, i
        while left < right:
            mid = (left + right) // 2
            if arr[mid] <= key:
                left = mid + 1
            else:
                right = mid
        
        # Shift elements and insert
        for j in range(i, left, -1):
            arr[j] = arr[j - 1]
        arr[left] = key
    
    return arr


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [12, 11, 13, 5, 6],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Insertion Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        sorted_arr = insertion_sort(arr)
        print(f"Original: {arr}")
        print(f"Sorted:   {sorted_arr}")
        print()

