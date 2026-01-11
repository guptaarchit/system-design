"""
Bucket Sort Algorithm

Bucket Sort is a sorting algorithm that works by distributing the elements of an array
into a number of buckets. Each bucket is then sorted individually, either using a
different sorting algorithm, or by recursively applying the bucket sorting algorithm.

It is a distribution sort, a generalization of pigeonhole sort, and is a cousin of
radix sort in the most-to-least significant digit flavor.

Time Complexity:
    - Best Case: O(n + k) - when elements are uniformly distributed
    - Average Case: O(n + k)
    - Worst Case: O(n²) - when all elements go to same bucket

Space Complexity: O(n + k) where k is number of buckets

Stable: Yes (if stable sorting algorithm used for buckets)

Use Cases:
    - When input is uniformly distributed over a range
    - Floating point numbers in range [0.0, 1.0)
    - When data can be partitioned into buckets
"""


def bucket_sort(arr, num_buckets=None):
    """
    Sort an array using Bucket Sort algorithm.
    Assumes elements are in range [0, 1) or can be normalized.
    
    Args:
        arr: List of floating point numbers in range [0, 1)
        num_buckets: Number of buckets (defaults to len(arr))
        
    Returns:
        Sorted list
        
    Example:
        >>> bucket_sort([0.897, 0.565, 0.656, 0.1234, 0.665, 0.3434])
        [0.1234, 0.3434, 0.565, 0.656, 0.665, 0.897]
    """
    if not arr:
        return []
    
    arr = arr.copy()
    n = len(arr)
    
    if num_buckets is None:
        num_buckets = n
    
    # Create empty buckets
    buckets = [[] for _ in range(num_buckets)]
    
    # Insert elements into buckets
    for num in arr:
        bucket_index = int(num * num_buckets)
        # Handle edge case for 1.0
        if bucket_index == num_buckets:
            bucket_index = num_buckets - 1
        buckets[bucket_index].append(num)
    
    # Sort individual buckets (using insertion sort)
    for bucket in buckets:
        insertion_sort_bucket(bucket)
    
    # Concatenate all buckets into arr[]
    result = []
    for bucket in buckets:
        result.extend(bucket)
    
    return result


def insertion_sort_bucket(bucket):
    """
    Insertion sort for sorting individual buckets.
    
    Args:
        bucket: List to sort (modified in place)
    """
    for i in range(1, len(bucket)):
        key = bucket[i]
        j = i - 1
        while j >= 0 and bucket[j] > key:
            bucket[j + 1] = bucket[j]
            j -= 1
        bucket[j + 1] = key


def bucket_sort_integers(arr, num_buckets=None):
    """
    Bucket Sort for integers.
    
    Args:
        arr: List of integers
        num_buckets: Number of buckets
        
    Returns:
        Sorted list
    """
    if not arr:
        return []
    
    arr = arr.copy()
    n = len(arr)
    
    if num_buckets is None:
        num_buckets = n
    
    # Find min and max values
    min_val = min(arr)
    max_val = max(arr)
    
    if min_val == max_val:
        return arr
    
    # Create buckets
    buckets = [[] for _ in range(num_buckets)]
    
    # Calculate range for each bucket
    bucket_range = (max_val - min_val + 1) / num_buckets
    
    # Distribute elements into buckets
    for num in arr:
        bucket_index = int((num - min_val) / bucket_range)
        if bucket_index == num_buckets:
            bucket_index = num_buckets - 1
        buckets[bucket_index].append(num)
    
    # Sort buckets and concatenate
    result = []
    for bucket in buckets:
        if bucket:
            # Use insertion sort for small buckets, or any other sort
            insertion_sort_bucket(bucket)
            result.extend(bucket)
    
    return result


def bucket_sort_general(arr, num_buckets=None, key_func=None):
    """
    General bucket sort that works with any comparable elements.
    
    Args:
        arr: List of elements
        num_buckets: Number of buckets
        key_func: Function to extract numeric key from element
        
    Returns:
        Sorted list
    """
    if not arr:
        return []
    
    arr = arr.copy()
    n = len(arr)
    
    if num_buckets is None:
        num_buckets = n
    
    if key_func is None:
        key_func = lambda x: x
    
    # Extract keys and find range
    keys = [key_func(x) for x in arr]
    min_key = min(keys)
    max_key = max(keys)
    
    if min_key == max_key:
        return arr
    
    # Create buckets
    buckets = [[] for _ in range(num_buckets)]
    bucket_range = (max_key - min_key + 1) / num_buckets
    
    # Distribute elements
    for i, elem in enumerate(arr):
        bucket_index = int((keys[i] - min_key) / bucket_range)
        if bucket_index == num_buckets:
            bucket_index = num_buckets - 1
        buckets[bucket_index].append(elem)
    
    # Sort buckets and concatenate
    result = []
    for bucket in buckets:
        if bucket:
            # Sort bucket using insertion sort or any stable sort
            insertion_sort_bucket(bucket)
            result.extend(bucket)
    
    return result


if __name__ == "__main__":
    # Example usage
    print("Bucket Sort Examples:")
    print("=" * 50)
    
    # Floating point numbers in [0, 1)
    float_array = [0.897, 0.565, 0.656, 0.1234, 0.665, 0.3434]
    print(f"Original (floats): {float_array}")
    sorted_floats = bucket_sort(float_array)
    print(f"Sorted:            {sorted_floats}")
    print()
    
    # Integers
    int_array = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original (ints):   {int_array}")
    sorted_ints = bucket_sort_integers(int_array)
    print(f"Sorted:            {sorted_ints}")
    print()
    
    # Empty array
    print(f"Original (empty):  []")
    sorted_empty = bucket_sort([])
    print(f"Sorted:            {sorted_empty}")

