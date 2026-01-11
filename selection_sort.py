"""
Selection Sort Algorithm

Selection Sort is an in-place comparison sorting algorithm. It divides the input
list into two parts: a sorted sublist of items built up from left to right at the
front (left) of the list, and a sublist of the remaining unsorted items.

The algorithm finds the minimum element in the unsorted sublist and swaps it with
the leftmost unsorted element, moving the sublist boundaries one element to the right.

Time Complexity:
    - Best Case: O(n²)
    - Average Case: O(n²)
    - Worst Case: O(n²)

Space Complexity: O(1) - in-place sorting

Stable: No (may change relative order of equal elements)

Use Cases:
    - When memory write is a costly operation
    - Small datasets
    - When simplicity is preferred over efficiency
"""


def selection_sort(arr):
    """
    Sort an array using Selection Sort algorithm.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
        
    Example:
        >>> selection_sort([64, 25, 12, 22, 11])
        [11, 12, 22, 25, 64]
    """
    arr = arr.copy()  # Don't modify original array
    n = len(arr)
    
    # Traverse through all array elements
    for i in range(n):
        # Find the minimum element in remaining unsorted array
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        
        # Swap the found minimum element with the first element
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    
    return arr


def selection_sort_stable(arr):
    """
    Stable version of Selection Sort.
    Instead of swapping, it pushes elements to make room for the minimum.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list (stable)
    """
    arr = arr.copy()
    n = len(arr)
    
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        
        # Instead of swapping, shift elements and insert minimum
        min_value = arr[min_idx]
        for k in range(min_idx, i, -1):
            arr[k] = arr[k - 1]
        arr[i] = min_value
    
    return arr


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [64, 25, 12, 22, 11],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Selection Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        sorted_arr = selection_sort(arr)
        print(f"Original: {arr}")
        print(f"Sorted:   {sorted_arr}")
        print()

