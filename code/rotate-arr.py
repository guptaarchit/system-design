# 189. Rotate Array
# Attempted
# Medium
# Topics
# Companies
# Hint
# Given an integer array nums, rotate the array to the right by k steps, where k is non-negative.

# Example 1:
# Input: nums = [1,2,3,4,5,6,7], k = 3
# Output: [5,6,7,1,2,3,4]
# Explanation:
# rotate 1 steps to the right: [7,1,2,3,4,5,6]
# rotate 2 steps to the right: [6,7,1,2,3,4,5]
# rotate 3 steps to the right: [5,6,7,1,2,3,4]

# Example 2:
# Input: nums = [-1,-100,3,99], k = 2
# Output: [3,99,-1,-100]
# Explanation: 
# rotate 1 steps to the right: [99,-1,-100,3]
# rotate 2 steps to the right: [3,99,-1,-100]

# Constraints:
# 1 <= nums.length <= 105
# -231 <= nums[i] <= 231 - 1
# 0 <= k <= 105

# Follow up:
# Try to come up with as many solutions as you can. There are at least three different ways to solve this problem.
# Could you do it in-place with O(1) extra space?


# Code - Solution 1: Reverse Approach (Optimal - O(1) space)
class Solution:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Rotate array to the right by k steps using reverse approach.
        
        Approach: Reverse Three Times
        1. Reverse the entire array
        2. Reverse the first k elements
        3. Reverse the remaining elements
        
        Time Complexity: O(n)
        Space Complexity: O(1)
        
        Example: nums = [1,2,3,4,5,6,7], k = 3
        Step 1: Reverse entire array → [7,6,5,4,3,2,1]
        Step 2: Reverse first k=3 → [5,6,7,4,3,2,1]
        Step 3: Reverse remaining n-k=4 → [5,6,7,1,2,3,4] ✓
        """
        n = len(nums)
        k = k % n  # Handle k >= n (e.g., k=10, n=7 → k=3)
        
        # Reverse entire array
        self._reverse(nums, 0, n - 1)
        # Reverse first k elements
        self._reverse(nums, 0, k - 1)
        # Reverse remaining elements
        self._reverse(nums, k, n - 1)
    
    def _reverse(self, nums: list[int], start: int, end: int) -> None:
        """Helper function to reverse array from start to end."""
        while start < end:
            nums[start], nums[end] = nums[end], nums[start]
            start += 1
            end -= 1


# Code - Solution 2: Using Extra Array (Simple - O(n) space)
class Solution2:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Rotate array using extra array.
        
        Approach: Create new array with rotated elements
        - New position: (i + k) % n
        
        Time Complexity: O(n)
        Space Complexity: O(n)
        
        Example: nums = [1,2,3,4,5,6,7], k = 3
        new_nums[0] = nums[(0-3+7)%7] = nums[4] = 5
        new_nums[1] = nums[(1-3+7)%7] = nums[5] = 6
        new_nums[2] = nums[(2-3+7)%7] = nums[6] = 7
        new_nums[3] = nums[(3-3+7)%7] = nums[0] = 1
        ...
        Result: [5,6,7,1,2,3,4]
        """
        n = len(nums)
        k = k % n
        rotated = [0] * n
        
        for i in range(n):
            rotated[(i + k) % n] = nums[i]
        
        # Copy back to original array
        for i in range(n):
            nums[i] = rotated[i]


# Code - Solution 3: Cyclic Replacements (O(1) space)
class Solution3:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Rotate array using cyclic replacements.
        
        Approach: Move elements in cycles
        - Start from index 0, move element to (i+k) % n
        - Continue until we've moved all n elements
        
        Time Complexity: O(n)
        Space Complexity: O(1)
        
        Example: nums = [1,2,3,4], k = 2
        Cycle 1: 0 → 2 → 0 (back to start, move to next)
        Cycle 2: 1 → 3 → 1 (back to start, done)
        """
        n = len(nums)
        k = k % n
        
        if k == 0:
            return
        
        count = 0  # Track how many elements we've moved
        start = 0
        
        while count < n:
            current = start
            prev = nums[start]
            
            while True:
                next_idx = (current + k) % n
                # Store the element that will be overwritten
                temp = nums[next_idx]
                # Place previous element
                nums[next_idx] = prev
                prev = temp
                current = next_idx
                count += 1
                
                # If we've come back to start, break and move to next cycle
                if current == start:
                    break
            
            start += 1


# Code - Solution 4: Rotate k Times (Simple but Slow)
class Solution4:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Rotate array by rotating one step at a time, k times.
        
        Approach: Rotate one step to the right, repeat k times
        
        Time Complexity: O(n * k) - slow for large k
        Space Complexity: O(1)
        
        Example: nums = [1,2,3,4], k = 2
        Step 1: [4,1,2,3]
        Step 2: [3,4,1,2]
        """
        n = len(nums)
        k = k % n
        
        for _ in range(k):
            # Rotate one step to the right
            last = nums[-1]
            for i in range(n - 1, 0, -1):
                nums[i] = nums[i - 1]
            nums[0] = last


# Code - Solution 5: Using Slicing (Pythonic)
class Solution5:
    def rotate(self, nums: list[int], k: int) -> None:
        """
        Rotate array using Python slicing.
        
        Approach: Slice and concatenate
        
        Time Complexity: O(n)
        Space Complexity: O(n) - creates new list
        
        Example: nums = [1,2,3,4,5,6,7], k = 3
        nums[:] = nums[-3:] + nums[:-3]
        nums[:] = [5,6,7] + [1,2,3,4] = [5,6,7,1,2,3,4]
        
        IMPORTANT: Understanding nums[:] vs nums =
        -----------------------------------------
        nums[:] is a slice assignment that modifies the list IN-PLACE.
        nums = ... creates a new list and reassigns the local variable.
        
        Example:
        def modify_list(nums):
            nums[:] = [1, 2, 3]  # Modifies the original list
            # OR
            nums = [1, 2, 3]     # Only changes local variable, original unchanged!
        
        arr = [4, 5, 6]
        modify_list(arr)
        # With nums[:]: arr becomes [1, 2, 3] ✓
        # With nums =: arr stays [4, 5, 6] ✗
        
        Why use nums[:]?
        - The function signature says "modify nums in-place" (return None)
        - nums[:] replaces all elements of the existing list
        - This is required for LeetCode problems that check the original array
        """
        n = len(nums)
        k = k % n
        nums[:] = nums[-k:] + nums[:-k]


# Note
# Algorithm Comparison:
#
# Solution 1: Reverse Approach (RECOMMENDED)
# - Time: O(n), Space: O(1)
# - Elegant and efficient
# - Key insight: Reversing three times achieves rotation
#
# Solution 2: Extra Array
# - Time: O(n), Space: O(n)
# - Simple and easy to understand
# - Good for when space is not a concern
#
# Solution 3: Cyclic Replacements
# - Time: O(n), Space: O(1)
# - More complex but space-efficient
# - Handles cycles correctly
#
# Solution 4: Rotate k Times
# - Time: O(n*k), Space: O(1)
# - Simple but inefficient for large k
# - Not recommended for production
#
# Solution 5: Slicing (Pythonic)
# - Time: O(n), Space: O(n)
# - Very concise in Python
# - Creates new list internally
#
# Key Insight: k % n handles cases where k >= n
# Example: k=10, n=7 → k=3 (rotating 10 steps = rotating 3 steps)


# Testcase
def test_rotate():
    solution1 = Solution()
    solution2 = Solution2()
    solution3 = Solution3()
    solution4 = Solution4()
    solution5 = Solution5()
    
    solutions = [solution1, solution2, solution3, solution4, solution5]
    
    # Test case 1
    nums = [1, 2, 3, 4, 5, 6, 7]
    expected = [5, 6, 7, 1, 2, 3, 4]
    for i, sol in enumerate(solutions, 1):
        test_nums = nums.copy()
        sol.rotate(test_nums, 3)
        assert test_nums == expected, f"Solution {i} failed: got {test_nums}, expected {expected}"
    
    # Test case 2
    nums = [-1, -100, 3, 99]
    expected = [3, 99, -1, -100]
    for i, sol in enumerate(solutions, 1):
        test_nums = nums.copy()
        sol.rotate(test_nums, 2)
        assert test_nums == expected, f"Solution {i} failed: got {test_nums}, expected {expected}"
    
    # Test case 3: k = 0 (no rotation)
    nums = [1, 2, 3]
    expected = [1, 2, 3]
    for i, sol in enumerate(solutions, 1):
        test_nums = nums.copy()
        sol.rotate(test_nums, 0)
        assert test_nums == expected, f"Solution {i} failed"
    
    # Test case 4: k >= n (k = n, should be same as k = 0)
    nums = [1, 2, 3]
    expected = [1, 2, 3]
    for i, sol in enumerate(solutions, 1):
        test_nums = nums.copy()
        sol.rotate(test_nums, 3)
        assert test_nums == expected, f"Solution {i} failed"
    
    # Test case 5: k > n
    nums = [1, 2]
    expected = [2, 1]  # k=3, n=2 → k=1
    for i, sol in enumerate(solutions, 1):
        test_nums = nums.copy()
        sol.rotate(test_nums, 3)
        assert test_nums == expected, f"Solution {i} failed"
    
    # Test case 6: Single element
    nums = [1]
    expected = [1]
    for i, sol in enumerate(solutions, 1):
        test_nums = nums.copy()
        sol.rotate(test_nums, 5)
        assert test_nums == expected, f"Solution {i} failed"
    
    print("All test cases passed for all solutions!")


# Test Result
if __name__ == "__main__":
    test_rotate()