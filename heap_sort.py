"""
Heap Sort Algorithm

Heap Sort is a comparison-based sorting technique based on Binary Heap data structure.
It is similar to selection sort where we first find the maximum element and place it
at the end. We repeat the same process for the remaining elements.

A Binary Heap is a Complete Binary Tree where items are stored in a special order
such that the value in a parent node is greater (or smaller) than the values in its
two children nodes. The former is called max heap and the latter is called min heap.

Time Complexity:
    - Best Case: O(n log n)
    - Average Case: O(n log n)
    - Worst Case: O(n log n)

Space Complexity: O(1) - in-place sorting

Stable: No

Use Cases:
    - When worst-case O(n log n) is required
    - When in-place sorting is preferred
    - Priority queue implementations
    - Finding k largest/smallest elements
"""


def heap_sort(arr):
    """
    Sort an array using Heap Sort algorithm.
    
    Args:
        arr: List of comparable elements
        
    Returns:
        Sorted list
        
    Example:
        >>> heap_sort([12, 11, 13, 5, 6, 7])
        [5, 6, 7, 11, 12, 13]
    """
    arr = arr.copy()
    n = len(arr)
    
    # Build a max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    # One by one extract elements from heap
    for i in range(n - 1, 0, -1):
        # Move current root to end
        arr[0], arr[i] = arr[i], arr[0]
        
        # Call max heapify on the reduced heap
        heapify(arr, i, 0)
    
    return arr


def heapify(arr, n, i):
    """
    Heapify a subtree rooted at index i.
    Assumes that the subtrees are already heapified.
    
    Args:
        arr: Array representing the heap
        n: Size of heap
        i: Root index of subtree
    """
    largest = i  # Initialize largest as root
    left = 2 * i + 1  # Left child
    right = 2 * i + 2  # Right child
    
    # If left child is larger than root
    if left < n and arr[left] > arr[largest]:
        largest = left
    
    # If right child is larger than largest so far
    if right < n and arr[right] > arr[largest]:
        largest = right
    
    # If largest is not root
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        
        # Recursively heapify the affected sub-tree
        heapify(arr, n, largest)


class MinHeap:
    """Min Heap implementation for sorting in descending order."""
    
    def __init__(self, arr):
        self.heap = arr.copy()
        self.size = len(arr)
        self._build_heap()
    
    def _build_heap(self):
        """Build min heap from array."""
        for i in range(self.size // 2 - 1, -1, -1):
            self._heapify_down(i)
    
    def _heapify_down(self, i):
        """Heapify down from index i."""
        smallest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < self.size and self.heap[left] < self.heap[smallest]:
            smallest = left
        
        if right < self.size and self.heap[right] < self.heap[smallest]:
            smallest = right
        
        if smallest != i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self._heapify_down(smallest)
    
    def extract_min(self):
        """Extract minimum element."""
        if self.size == 0:
            return None
        
        min_val = self.heap[0]
        self.heap[0] = self.heap[self.size - 1]
        self.size -= 1
        self._heapify_down(0)
        return min_val


def heap_sort_descending(arr):
    """
    Sort array in descending order using min heap.
    
    Args:
        arr: List to sort
        
    Returns:
        List sorted in descending order
    """
    min_heap = MinHeap(arr)
    result = []
    
    for _ in range(len(arr)):
        result.append(min_heap.extract_min())
    
    return result


if __name__ == "__main__":
    # Example usage
    test_arrays = [
        [12, 11, 13, 5, 6, 7],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        []  # Empty array
    ]
    
    print("Heap Sort Examples:")
    print("=" * 50)
    
    for arr in test_arrays:
        sorted_arr = heap_sort(arr)
        print(f"Original: {arr}")
        print(f"Sorted:   {sorted_arr}")
        print()

