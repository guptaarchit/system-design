# 503. Next Greater Element II
# Medium
# Topics
# conpanies icon
# Companies
# Given a circular integer array nums (i.e., the next element of nums[nums.length - 1] is nums[0]), return the next greater number for every element in nums.

# The next greater number of a number x is the first greater number to its traversing-order next in the array, which means you could search circularly to find its next greater number. If it doesn't exist, return -1 for this number.

 

# Example 1:

# Input: nums = [1,2,1]
# Output: [2,-1,2]
# Explanation: The first 1's next greater number is 2; 
# The number 2 can't find next greater number. 
# The second 1's next greater number needs to search circularly, which is also 2.
# Example 2:

# Input: nums = [1,2,3,4,3]
# Output: [2,3,4,-1,4]
 

# Constraints:

# 1 <= nums.length <= 104
# -109 <= nums[i] <= 109

"""
PROBLEM EXPLANATION:
===================

Given a CIRCULAR array, for each element, find the NEXT GREATER ELEMENT.

What does "circular" mean?
- After the last element, we wrap around to the first element
- Think of it as a circle: [1,2,3] → 1→2→3→1→2→3→...

What is "next greater element"?
- For each element nums[i], find the first element to its right (or wrapping around)
  that is GREATER than nums[i]
- If no greater element exists, return -1

DETAILED EXAMPLE BREAKDOWN:
===========================

Example 1: nums = [1, 2, 1]
Index 0 (value 1):
  - Look right: [2, 1] → first greater is 2 at index 1
  - Result: 2

Index 1 (value 2):
  - Look right: [1] → no greater element
  - Wrap around: [1] → still no greater element
  - Result: -1

Index 2 (value 1):
  - Look right: [] → wrap around to [1, 2]
  - First greater is 2 at index 1 (after wrapping)
  - Result: 2

Output: [2, -1, 2]

Example 2: nums = [1, 2, 3, 4, 3]
Index 0 (value 1): Next greater is 2 → [2]
Index 1 (value 2): Next greater is 3 → [2, 3]
Index 2 (value 3): Next greater is 4 → [2, 3, 4]
Index 3 (value 4): 
  - Look right: [3] → no greater
  - Wrap around: [1, 2, 3] → no greater
  - Result: -1
Index 4 (value 3):
  - Look right: [] → wrap around to [1, 2, 3, 4]
  - First greater is 4 at index 3 (after wrapping)
  - Result: 4

Output: [2, 3, 4, -1, 4]

KEY INSIGHT:
============
Since the array is circular, we can traverse it TWICE to simulate wrapping around.
We can use a monotonic stack to efficiently find the next greater element.

APPROACH:
=========
1. Use a stack to store indices of elements we haven't found answers for yet
2. Traverse the array TWICE (to handle circularity)
3. For each element:
   - While stack is not empty and current element > element at stack top:
     * Pop from stack
     * Set result[popped_index] = current element
   - Push current index to stack
4. After two passes, remaining elements in stack have no greater element → set to -1
"""


class Solution:
    def nextGreaterElements(self, nums: list[int]) -> list[int]:
        """
        Find next greater element for each element in circular array.
        
        Algorithm:
        1. Initialize result array with -1
        2. Use stack to store indices of elements waiting for their next greater
        3. Traverse array TWICE (simulates circular wrap-around)
        4. For each element:
           - While stack not empty and current > nums[stack[-1]]:
             * Pop index from stack
             * Set result[popped_index] = current element
           - Push current index to stack
        
        Time: O(n) - each element pushed/popped at most twice
        Space: O(n) - stack and result array
        """
        n = len(nums)
        result = [-1] * n
        stack = []
        
        # Traverse twice to handle circular array
        for i in range(2 * n):
            # Use modulo to wrap around: i % n gives actual index
            actual_idx = i % n
            
            # While stack has elements and current is greater than top element
            while stack and nums[actual_idx] > nums[stack[-1]]:
                # Pop index and set its result
                popped_idx = stack.pop()
                result[popped_idx] = nums[actual_idx]
            
            # Only push during first pass (to avoid duplicate processing)
            if i < n:
                stack.append(actual_idx)
        
        return result


# Alternative approach: More explicit two-pass
class SolutionTwoPass:
    def nextGreaterElements(self, nums: list[int]) -> list[int]:
        """
        Two-pass approach - more explicit about handling circularity.
        """
        n = len(nums)
        result = [-1] * n
        stack = []
        
        # First pass: handle non-circular next greater elements
        for i in range(n):
            while stack and nums[i] > nums[stack[-1]]:
                popped_idx = stack.pop()
                result[popped_idx] = nums[i]
            stack.append(i)
        
        # Second pass: handle circular wrap-around
        for i in range(n):
            while stack and nums[i] > nums[stack[-1]]:
                popped_idx = stack.pop()
                result[popped_idx] = nums[i]
            # Don't push again - we've already processed all indices
        
        return result


# Test cases
if __name__ == "__main__":
    solution = Solution()
    solution2 = SolutionTwoPass()
    
    # Example 1: [1,2,1] -> [2,-1,2]
    result1 = solution.nextGreaterElements([1, 2, 1])
    assert result1 == [2, -1, 2]
    assert solution2.nextGreaterElements([1, 2, 1]) == [2, -1, 2]
    print("Example 1 passed: [1,2,1] -> [2,-1,2]")
    
    # Example 2: [1,2,3,4,3] -> [2,3,4,-1,4]
    result2 = solution.nextGreaterElements([1, 2, 3, 4, 3])
    assert result2 == [2, 3, 4, -1, 4]
    assert solution2.nextGreaterElements([1, 2, 3, 4, 3]) == [2, 3, 4, -1, 4]
    print("Example 2 passed: [1,2,3,4,3] -> [2,3,4,-1,4]")
    
    # Additional test cases
    result3 = solution.nextGreaterElements([5, 4, 3, 2, 1])
    assert result3 == [-1, 5, 5, 5, 5]
    assert solution2.nextGreaterElements([5, 4, 3, 2, 1]) == [-1, 5, 5, 5, 5]
    print("Additional test passed: [5,4,3,2,1] -> [-1,5,5,5,5]")
    
    result4 = solution.nextGreaterElements([1, 1, 1, 1])
    assert result4 == [-1, -1, -1, -1]
    assert solution2.nextGreaterElements([1, 1, 1, 1]) == [-1, -1, -1, -1]
    print("Additional test passed: [1,1,1,1] -> [-1,-1,-1,-1]")
    
    result5 = solution.nextGreaterElements([1])
    assert result5 == [-1]
    assert solution2.nextGreaterElements([1]) == [-1]
    print("Additional test passed: [1] -> [-1]")
    
    print("\nAll test cases passed!")