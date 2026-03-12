# 88. Merge Sorted Array
# Easy
# Topics
# Companies
# You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, 
# and two integers m and n, representing the number of elements in nums1 and nums2 respectively.
# 
# Merge nums2 into nums1 as one sorted array.
# 
# The final sorted array should not be returned by the function, but instead be stored 
# inside the array nums1. To accommodate this, nums1 has a length of m + n, where 
# the first m elements denote the elements that should be merged, and the last n elements 
# are set to 0 and should be ignored. nums2 has a length of n.
#
# Example 1:
# Input: nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
# Output: [1,2,2,3,5,6]
# Explanation: The arrays we are merging are [1,2,3] and [2,5,6].
# The result of the merge is [1,2,2,3,5,6] with the underlined elements coming from nums1.
#
# Example 2:
# Input: nums1 = [1], m = 1, nums2 = [], n = 0
# Output: [1]
# Explanation: The arrays we are merging are [1] and [].
# The result of the merge is [1].
#
# Example 3:
# Input: nums1 = [0], m = 0, nums2 = [1], n = 1
# Output: [1]
# Explanation: The arrays we are merging are [] and [1].
# The result of the merge is [1].
#
# Constraints:
# nums1.length == m + n
# nums2.length == n
# 0 <= m, n <= 200
# 1 <= m + n <= 200
# -109 <= nums1[i], nums2[j] <= 109


# Code - Solution 1: Two Pointers from End (Optimal - In-place)
class Solution:
    def merge(self, nums1: list[int], m: int, nums2: list[int], n: int) -> None:
        """
        Merge nums2 into nums1 in-place as one sorted array.
        
        Approach: Two Pointers from End
        - Start from the end of both arrays
        - Compare elements and place larger one at the end of nums1
        - This avoids overwriting unprocessed elements in nums1
        
        Time Complexity: O(m + n)
        Space Complexity: O(1)
        
        Example walkthrough:
        nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
        
        i = m-1 = 2 (last element in nums1)
        j = n-1 = 2 (last element in nums2)
        k = m+n-1 = 5 (last position in nums1)
        
        Step 1: nums1[2]=3, nums2[2]=6 → 6 > 3 → nums1[5]=6, j=1, k=4
        nums1 = [1,2,3,0,0,6]
        
        Step 2: nums1[2]=3, nums2[1]=5 → 5 > 3 → nums1[4]=5, j=0, k=3
        nums1 = [1,2,3,0,5,6]
        
        Step 3: nums1[2]=3, nums2[0]=2 → 3 > 2 → nums1[3]=3, i=1, k=2
        nums1 = [1,2,3,3,5,6]
        
        Step 4: nums1[1]=2, nums2[0]=2 → 2 == 2 → nums1[2]=2, j=-1, k=1
        nums1 = [1,2,2,3,5,6]
        
        Step 5: j < 0, copy remaining nums1[0:2] → done
        Final: [1,2,2,3,5,6]
        """
        # Two pointers starting from the end
        i = m - 1  # Last element in nums1's valid range
        j = n - 1  # Last element in nums2
        k = m + n - 1  # Last position in nums1
        
        # Merge from the end
        while i >= 0 and j >= 0:
            if nums1[i] > nums2[j]:
                nums1[k] = nums1[i]
                i -= 1
            else:
                nums1[k] = nums2[j]
                j -= 1
            k -= 1
        
        # Copy remaining elements from nums2 (if any)
        # No need to copy remaining nums1 elements as they're already in place
        while j >= 0:
            nums1[k] = nums2[j]
            j -= 1
            k -= 1


# Code - Solution 2: General Merge Function (Returns New Array)
class Solution2:
    def mergeSortedArrays(self, nums1: list[int], nums2: list[int]) -> list[int]:
        """
        Merge two sorted arrays into a new sorted array.
        
        Approach: Two Pointers from Start
        - Use two pointers starting from the beginning
        - Compare elements and add smaller one to result
        - Copy remaining elements
        
        Time Complexity: O(m + n)
        Space Complexity: O(m + n) for the result array
        
        Example:
        nums1 = [1, 2, 3], nums2 = [2, 5, 6]
        Result: [1, 2, 2, 3, 5, 6]
        """
        result = []
        i, j = 0, 0
        
        # Merge while both arrays have elements
        while i < len(nums1) and j < len(nums2):
            if nums1[i] <= nums2[j]:
                result.append(nums1[i])
                i += 1
            else:
                result.append(nums2[j])
                j += 1
        
        # Add remaining elements
        result.extend(nums1[i:])
        result.extend(nums2[j:])
        
        return result


# Code - Solution 3: Using Built-in Sort (Not Optimal, but Simple)
class Solution3:
    def merge(self, nums1: list[int], m: int, nums2: list[int], n: int) -> None:
        """
        Simple approach: copy nums2 into nums1 and sort.
        Not optimal but easy to understand.
        
        Time Complexity: O((m+n) log(m+n))
        Space Complexity: O(1) excluding the sort space
        """
        # Copy nums2 into the end of nums1
        for i in range(n):
            nums1[m + i] = nums2[i]
        
        # Sort the entire array
        nums1.sort()


# Note
# Algorithm: Two Pointers from End (Optimal)
# Key insight: Start merging from the end to avoid overwriting unprocessed elements.
#
# Steps:
# 1. Initialize three pointers:
#    - i: last valid element in nums1 (m-1)
#    - j: last element in nums2 (n-1)
#    - k: last position in nums1 (m+n-1)
# 2. Compare nums1[i] and nums2[j]
# 3. Place the larger element at nums1[k]
# 4. Move pointers accordingly
# 5. Copy remaining elements from nums2 if any
#
# Why start from the end?
# - If we start from the beginning, we'd overwrite elements in nums1 that haven't been processed yet
# - Starting from the end uses the extra space (zeros) at the end of nums1
#
# Time Complexity: O(m + n) - single pass through both arrays
# Space Complexity: O(1) - only using a few variables


# Testcase
def test_merge():
    solution = Solution()
    solution2 = Solution2()
    solution3 = Solution3()
    
    # Test case 1
    nums1 = [1, 2, 3, 0, 0, 0]
    solution.merge(nums1, 3, [2, 5, 6], 3)
    assert nums1 == [1, 2, 2, 3, 5, 6]
    
    nums1_copy = [1, 2, 3, 0, 0, 0]
    solution3.merge(nums1_copy, 3, [2, 5, 6], 3)
    assert nums1_copy == [1, 2, 2, 3, 5, 6]
    
    result = solution2.mergeSortedArrays([1, 2, 3], [2, 5, 6])
    assert result == [1, 2, 2, 3, 5, 6]
    
    # Test case 2
    nums1 = [1]
    solution.merge(nums1, 1, [], 0)
    assert nums1 == [1]
    
    result = solution2.mergeSortedArrays([1], [])
    assert result == [1]
    
    # Test case 3
    nums1 = [0]
    solution.merge(nums1, 0, [1], 1)
    assert nums1 == [1]
    
    result = solution2.mergeSortedArrays([], [1])
    assert result == [1]
    
    # Test case 4: nums1 is empty
    nums1 = [0, 0]
    solution.merge(nums1, 0, [1, 2], 2)
    assert nums1 == [1, 2]
    
    # Test case 5: nums2 is empty
    nums1 = [1, 2]
    solution.merge(nums1, 2, [], 0)
    assert nums1 == [1, 2]
    
    # Test case 6: All elements in nums2 are smaller
    nums1 = [4, 5, 6, 0, 0, 0]
    solution.merge(nums1, 3, [1, 2, 3], 3)
    assert nums1 == [1, 2, 3, 4, 5, 6]
    
    # Test case 7: All elements in nums2 are larger
    nums1 = [1, 2, 3, 0, 0, 0]
    solution.merge(nums1, 3, [4, 5, 6], 3)
    assert nums1 == [1, 2, 3, 4, 5, 6]
    
    # Test case 8: Single elements
    nums1 = [2, 0]
    solution.merge(nums1, 1, [1], 1)
    assert nums1 == [1, 2]
    
    print("All test cases passed!")


# Test Result
if __name__ == "__main__":
    test_merge()