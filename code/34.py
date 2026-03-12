# 34. Find First and Last Position of Element in Sorted Array
# Solved
# Medium
# Topics
# conpanies icon
# Companies
# Given an array of integers nums sorted in non-decreasing order, find the starting and ending position of a given target value.

# If target is not found in the array, return [-1, -1].

# You must write an algorithm with O(log n) runtime complexity.

 

# Example 1:

# Input: nums = [5,7,7,8,8,10], target = 8
# Output: [3,4]
# Example 2:

# Input: nums = [5,7,7,8,8,10], target = 6
# Output: [-1,-1]
# Example 3:

# Input: nums = [], target = 0
# Output: [-1,-1]
 

# Constraints:

# 0 <= nums.length <= 105
# -109 <= nums[i] <= 109
# nums is a non-decreasing array.
# -109 <= target <= 109

from typing import List

class Solution:
    def searchRange(self, nums: List[int], target: int) -> List[int]:
        """
        Find first and last position of target in sorted array using binary search.
        Two modified binary searches: one for left boundary, one for right boundary.
        
        Time: O(log n), Space: O(1)
        """
        if not nums:
            return [-1, -1]
        
        def find_first():
            """Find leftmost index where nums[i] == target."""
            lo, hi = 0, len(nums) - 1
            result = -1
            while lo <= hi:
                mid = (lo + hi) // 2
                if nums[mid] == target:
                    result = mid
                    hi = mid - 1  # Keep searching left for earlier occurrence
                elif nums[mid] < target:
                    lo = mid + 1
                else:
                    hi = mid - 1
            return result
        
        def find_last():
            """Find rightmost index where nums[i] == target."""
            lo, hi = 0, len(nums) - 1
            result = -1
            while lo <= hi:
                mid = (lo + hi) // 2
                if nums[mid] == target:
                    result = mid
                    lo = mid + 1  # Keep searching right for later occurrence
                elif nums[mid] < target:
                    lo = mid + 1
                else:
                    hi = mid - 1
            return result
        
        return [find_first(), find_last()]