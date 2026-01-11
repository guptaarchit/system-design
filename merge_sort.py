"""
Merge Sort Algorithm

Merge Sort is a divide-and-conquer algorithm that divides the input array into
two halves, calls itself for the two halves, and then merges the two sorted halves.

The merge() function is used for merging two halves. The merge(arr, l, m, r) is
a key process that assumes that arr[l..m] and arr[m+1..r] are sorted and merges
the two sorted sub-arrays into one.

Time Complexity:
    - Best Case: O(n log n)
    - Average Case: O(n log n)
    - Worst Case: O(n log n)

Space Complexity: O(n) - requires temporary array for merging

Stable: Yes

Use Cases:
    - When stability is required
    - When worst-case O(n log n) is important
    - External sorting (sorting data that doesn't fit in memory)
    - Linked lists (efficient for linked lists)
"""


def merge_sort(arr):
    """
    Sort an array using Merge Sort algorithm.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
        
    Example:
        >>> merge_sort([38, 27, 43, 3, 9, 82, 10])
        [3, 9, 10, 27, 38, 43, 82]
    """
    if len(arr) <= 1:
        return arr.copy()
    
    # Divide the array into two halves
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Merge the sorted halves
    return merge(left, right)


def merge(left, right):
    """
    Merge two sorted arrays into a single sorted array.
    
    Args:
        left: Sorted left subarray
        right: Sorted right subarray
        
    Returns:
        Merged sorted array
    """
    result = []
    i = j = 0
    
    # Compare elements from both arrays and merge in sorted order
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # Add remaining elements
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result


def merge_sort_in_place(arr, left=0, right=None):
    """
    In-place merge sort (more memory efficient but complex).
    
    Args:
        arr: List to sort (will be modified)
        left: Starting index
        right: Ending index
        
    Returns:
        None (modifies array in place)
    """
    if right is None:
        right = len(arr) - 1
    
    if left < right:
        mid = (left + right) // 2
        
        # Sort first and second halves
        merge_sort_in_place(arr, left, mid)
        merge_sort_in_place(arr, mid + 1, right)
        
        # Merge the sorted halves
        merge_in_place(arr, left, mid, right)


def merge_in_place(arr, left, mid, right):
    """
    Merge two sorted subarrays in place.
    
    Args:
        arr: Array containing both subarrays
        left: Start index of first subarray
        mid: End index of first subarray
        right: End index of second subarray
    """
    # Create temporary arrays
    n1 = mid - left + 1
    n2 = right - mid
    
    L = [arr[left + i] for i in range(n1)]
    R = [arr[mid + 1 + j] for j in range(n2)]
    
    # Merge the temp arrays back into arr[left..right]
    i = j = 0
    k = left
    
    while i < n1 and j < n2:
        if L[i] <= R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1
    
    # Copy remaining elements
    while i < n1:
        arr[k] = L[i]
        i += 1
        k += 1
    
    while j < n2:
        arr[k] = R[j]
        j += 1
        k += 1


def merge_sort_iterative(arr):
    """
    Iterative (bottom-up) implementation of Merge Sort.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
    """
    arr = arr.copy()
    n = len(arr)
    
    # Start with subarrays of size 1, then double the size
    size = 1
    while size < n:
        for left in range(0, n - size, 2 * size):
            mid = left + size - 1
            right = min(left + 2 * size - 1, n - 1)
            merge_in_place(arr, left, mid, right)
        size *= 2
    
    return arr


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [38, 27, 43, 3, 9, 82, 10],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Merge Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        sorted_arr = merge_sort(arr)
        print(f"Original: {arr}")
        print(f"Sorted:   {sorted_arr}")
        print()

