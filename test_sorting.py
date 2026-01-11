"""
Test suite for all sorting algorithms.

This script tests all sorting algorithms to ensure they work correctly.
"""

import sys
from bubble_sort import bubble_sort
from selection_sort import selection_sort
from insertion_sort import insertion_sort
from merge_sort import merge_sort
from quick_sort import quick_sort
from heap_sort import heap_sort
from counting_sort import counting_sort
from radix_sort import radix_sort
from bucket_sort import bucket_sort, bucket_sort_integers


def test_sorting_algorithm(sort_func, name, test_cases):
    """Test a sorting algorithm with various test cases."""
    print(f"\nTesting {name}:")
    print("-" * 50)
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases):
        original = test_case.copy()
        try:
            result = sort_func(test_case)
            expected = sorted(original)
            
            if result == expected:
                print(f"✓ Test {i + 1} passed")
            else:
                print(f"✗ Test {i + 1} failed")
                print(f"  Input:    {original}")
                print(f"  Expected: {expected}")
                print(f"  Got:      {result}")
                all_passed = False
        except Exception as e:
            print(f"✗ Test {i + 1} raised exception: {e}")
            print(f"  Input: {original}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    # Test cases
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],  # Already sorted
        [5, 4, 3, 2, 1],  # Reverse sorted
        [42],  # Single element
        [],  # Empty array
        [3, 3, 3, 3],  # All same elements
        [1, 3, 2, 3, 1],  # Duplicates
    ]
    
    # Test cases for non-negative integers only
    non_negative_cases = [
        [4, 2, 2, 8, 3, 3, 1],
        [170, 45, 75, 90, 802, 24, 2, 66],
        [1, 0, 5, 2, 3],
    ]
    
    # Test cases for floats in [0, 1)
    float_cases = [
        [0.897, 0.565, 0.656, 0.1234, 0.665, 0.3434],
        [0.1, 0.5, 0.3, 0.2, 0.9],
    ]
    
    results = {}
    
    # Test comparison-based sorts
    comparison_sorts = [
        (bubble_sort, "Bubble Sort"),
        (selection_sort, "Selection Sort"),
        (insertion_sort, "Insertion Sort"),
        (merge_sort, "Merge Sort"),
        (quick_sort, "Quick Sort"),
        (heap_sort, "Heap Sort"),
    ]
    
    for sort_func, name in comparison_sorts:
        results[name] = test_sorting_algorithm(sort_func, name, test_cases)
    
    # Test counting sort (non-negative integers)
    results["Counting Sort"] = test_sorting_algorithm(
        counting_sort, "Counting Sort", non_negative_cases
    )
    
    # Test radix sort (non-negative integers)
    results["Radix Sort"] = test_sorting_algorithm(
        radix_sort, "Radix Sort", non_negative_cases
    )
    
    # Test bucket sort (integers)
    results["Bucket Sort (Integers)"] = test_sorting_algorithm(
        bucket_sort_integers, "Bucket Sort (Integers)", non_negative_cases
    )
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed! ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())

