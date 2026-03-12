# 53. Maximum Subarray
# Solved
# Medium
# Topics
# Companies
# Given an integer array nums, find the subarray with the largest sum, and return its sum.

# Example 1:
# Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
# Output: 6
# Explanation: The subarray [4,-1,2,1] has the largest sum 6.

# Example 2:
# Input: nums = [1]
# Output: 1
# Explanation: The subarray [1] has the largest sum 1.

# Example 3:
# Input: nums = [5,4,-1,7,8]
# Output: 23
# Explanation: The subarray [5,4,-1,7,8] has the largest sum 23.

# Constraints:
# 1 <= nums.length <= 105
# -104 <= nums[i] <= 104

# Follow up: If you have figured out the O(n) solution, try coding another solution 
# using the divide and conquer approach, which is more subtle.


# Code - Solution 1: Kadane's Algorithm (Optimal)
class Solution:
    def maxSubArray(self, nums: list[int]) -> int:
        """
        Find the maximum sum of a contiguous subarray using Kadane's algorithm.
        
        Algorithm: At each position, decide whether to extend the previous subarray
        or start a new one. If the current sum becomes negative, start fresh.
        
        Time Complexity: O(n)
        Space Complexity: O(1)
        """
        max_sum = nums[0]
        current_sum = nums[0]
        
        for i in range(1, len(nums)):
            # Either extend the previous subarray or start a new one
            current_sum = max(nums[i], current_sum + nums[i])
            max_sum = max(max_sum, current_sum)
        
        return max_sum


# Code - Solution 2: Divide and Conquer Approach
class Solution2:
    def maxSubArray(self, nums: list[int]) -> int:
        """
        Find the maximum sum using divide and conquer approach.
        
        Divide the array into two halves, recursively find max in each half,
        and also find max crossing the middle.
        
        Time Complexity: O(n log n)
        Space Complexity: O(log n) for recursion stack
        """
        return self._maxSubArrayHelper(nums, 0, len(nums) - 1)
    
    def _maxSubArrayHelper(self, nums: list[int], left: int, right: int) -> int:
        # Base case: single element
        if left == right:
            return nums[left]
        
        # Divide
        mid = (left + right) // 2
        
        # Conquer: find max in left and right halves
        left_max = self._maxSubArrayHelper(nums, left, mid)
        right_max = self._maxSubArrayHelper(nums, mid + 1, right)
        
        # Combine: find max crossing the middle
        cross_max = self._maxCrossingSum(nums, left, mid, right)
        
        # Return maximum of the three
        return max(left_max, right_max, cross_max)
    
    def _maxCrossingSum(self, nums: list[int], left: int, mid: int, right: int) -> int:
        """
        Find maximum sum of subarray crossing the middle point.
        """
        # Find max sum from mid to left
        left_sum = float('-inf')
        current_sum = 0
        for i in range(mid, left - 1, -1):
            current_sum += nums[i]
            left_sum = max(left_sum, current_sum)
        
        # Find max sum from mid+1 to right
        right_sum = float('-inf')
        current_sum = 0
        for i in range(mid + 1, right + 1):
            current_sum += nums[i]
            right_sum = max(right_sum, current_sum)
        
        # Return combined sum
        return left_sum + right_sum


# Code - Solution 3: Dynamic Programming (with tracking indices)
class Solution3:
    def maxSubArray(self, nums: list[int]) -> int:
        """
        Kadane's algorithm with ability to track the actual subarray indices.
        Returns both the max sum and the subarray boundaries.
        """
        max_sum = nums[0]
        current_sum = nums[0]
        # start = 0  # Uncomment if you need to track subarray start
        # end = 0    # Uncomment if you need to track subarray end
        temp_start = 0
        
        for i in range(1, len(nums)):
            if current_sum < 0:
                # Start a new subarray
                current_sum = nums[i]
                temp_start = i
            else:
                # Extend the current subarray
                current_sum += nums[i]
            
            if current_sum > max_sum:
                max_sum = current_sum
                # start = temp_start  # Uncomment if you need to track subarray start
                # end = i             # Uncomment if you need to track subarray end
        
        return max_sum
        # To return indices: uncomment start/end tracking above and return: max_sum, start, end


# Note
# Algorithm 1: Kadane's Algorithm (Recommended)
# Key insight: At each position, we decide whether to:
#   1. Extend the previous subarray (if current_sum >= 0)
#   2. Start a new subarray from current position (if current_sum < 0)
#
# The algorithm maintains:
#   - current_sum: maximum sum ending at current position
#   - max_sum: overall maximum sum seen so far
#
# Time: O(n), Space: O(1)
#
# Algorithm 2: Divide and Conquer
# Divide array into halves, recursively solve, then combine results.
# Need to handle three cases:
#   1. Max subarray in left half
#   2. Max subarray in right half  
#   3. Max subarray crossing the middle
#
# Time: O(n log n), Space: O(log n)


# Testcase
def test_maxSubArray():
    solution = Solution()
    solution2 = Solution2()
    solution3 = Solution3()
    
    # Test case 1
    nums1 = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    result1 = solution.maxSubArray(nums1)
    assert result1 == 6, f"Expected 6, got {result1}"
    assert solution2.maxSubArray(nums1) == 6
    assert solution3.maxSubArray(nums1) == 6
    
    # Test case 2
    nums2 = [1]
    result2 = solution.maxSubArray(nums2)
    assert result2 == 1, f"Expected 1, got {result2}"
    assert solution2.maxSubArray(nums2) == 1
    assert solution3.maxSubArray(nums2) == 1
    
    # Test case 3
    nums3 = [5, 4, -1, 7, 8]
    result3 = solution.maxSubArray(nums3)
    assert result3 == 23, f"Expected 23, got {result3}"
    assert solution2.maxSubArray(nums3) == 23
    assert solution3.maxSubArray(nums3) == 23
    
    # Test case 4: All negative
    nums4 = [-2, -1, -3]
    result4 = solution.maxSubArray(nums4)
    assert result4 == -1, f"Expected -1, got {result4}"
    assert solution2.maxSubArray(nums4) == -1
    assert solution3.maxSubArray(nums4) == -1
    
    # Test case 5: All positive
    nums5 = [1, 2, 3, 4]
    result5 = solution.maxSubArray(nums5)
    assert result5 == 10, f"Expected 10, got {result5}"
    assert solution2.maxSubArray(nums5) == 10
    assert solution3.maxSubArray(nums5) == 10
    
    # Test case 6: Single negative
    nums6 = [-1]
    result6 = solution.maxSubArray(nums6)
    assert result6 == -1, f"Expected -1, got {result6}"
    assert solution2.maxSubArray(nums6) == -1
    assert solution3.maxSubArray(nums6) == -1
    
    # Test case 7: Alternating positive and negative
    nums7 = [1, -2, 3, -4, 5]
    result7 = solution.maxSubArray(nums7)
    assert result7 == 5, f"Expected 5, got {result7}"
    assert solution2.maxSubArray(nums7) == 5
    assert solution3.maxSubArray(nums7) == 5
    
    print("All test cases passed!")


# Test Result
if __name__ == "__main__":
    test_maxSubArray()