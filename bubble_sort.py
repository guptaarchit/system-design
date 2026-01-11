"""
Bubble Sort Algorithm

Bubble Sort is a simple sorting algorithm that repeatedly steps through the list,
compares adjacent elements and swaps them if they are in the wrong order.
The pass through the list is repeated until the list is sorted.

Time Complexity:
    - Best Case: O(n) - when array is already sorted
    - Average Case: O(n²)
    - Worst Case: O(n²) - when array is reverse sorted

Space Complexity: O(1) - in-place sorting

Stable: Yes (maintains relative order of equal elements)

Use Cases:
    - Educational purposes
    - Small datasets
    - When simplicity is more important than efficiency
"""


def bubble_sort(arr):
    """
    Sort an array using Bubble Sort algorithm.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
        
    Example:
        >>> bubble_sort([64, 34, 25, 12, 22, 11, 90])
        [11, 12, 22, 25, 34, 64, 90]
    """
    arr = arr.copy()  # Don't modify original array
    n = len(arr)
    
    # Traverse through all array elements
    for i in range(n):
        swapped = False  # Optimization: check if any swap occurred
        
        # Last i elements are already in place
        for j in range(0, n - i - 1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater than the next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # If no two elements were swapped by inner loop, then break
        if not swapped:
            break
    
    return arr


def bubble_sort_recursive(arr, n=None):
    """
    Recursive implementation of Bubble Sort.
    
    Args:
        arr: List of comparable elements
        n: Length of array (optional, defaults to len(arr))
        
    Returns:
        Sorted list
    """
    if n is None:
        n = len(arr)
    
    # Base case
    if n == 1:
        return arr
    
    # One pass of bubble sort. After this pass, the largest element
    # is moved (or bubbled) to end.
    for i in range(n - 1):
        if arr[i] > arr[i + 1]:
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
    
    # Recur for remaining array
    return bubble_sort_recursive(arr, n - 1)


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Bubble Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        sorted_arr = bubble_sort(arr)
        print(f"Original: {arr}")
        print(f"Sorted:   {sorted_arr}")
        print()

