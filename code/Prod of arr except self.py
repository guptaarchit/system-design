# 238. Product of Array Except Self
# Medium
# Topics
# Companies
# Hint
# Given an integer array nums, return an array answer such that answer[i] is equal to 
# the product of all the elements of nums except nums[i].

# The product of any prefix or suffix of nums is guaranteed to fit in a 32-bit integer.

# You must write an algorithm that runs in O(n) time and without using the division operation.

# Example 1:
# Input: nums = [1,2,3,4]
# Output: [24,12,8,6]
# Explanation: 
# answer[0] = 2*3*4 = 24
# answer[1] = 1*3*4 = 12
# answer[2] = 1*2*4 = 8
# answer[3] = 1*2*3 = 6

# Example 2:
# Input: nums = [-1,1,0,-3,3]
# Output: [0,0,9,0,0]
# Explanation: Any product that includes 0 will be 0.

# Constraints:
# 2 <= nums.length <= 105
# -30 <= nums[i] <= 30
# The input is generated such that answer[i] is guaranteed to fit in a 32-bit integer.
 
# Follow up: Can you solve the problem in O(1) extra space complexity? 
# (The output array does not count as extra space for space complexity analysis.)


# Code - Solution 1: O(1) Extra Space (Optimal - Follow-up Answer)
class Solution:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        """
        Product of array except self using prefix and suffix products.
        
        Approach: Two Passes
        1. First pass: Store prefix products in result array
        2. Second pass: Multiply by suffix products using a running variable
        
        Time Complexity: O(n) - two passes through the array
        Space Complexity: O(1) - only using output array and one variable
        
        Example walkthrough for nums = [1,2,3,4]:
        Step 1: Calculate prefix products (left to right)
          result[0] = 1 (no elements before)
          result[1] = 1 (product of elements before index 1)
          result[2] = 1*2 = 2
          result[3] = 1*2*3 = 6
          result = [1, 1, 2, 6]
        
        Step 2: Multiply by suffix products (right to left)
          suffix = 1 (start from right)
          result[3] = 6 * 1 = 6 (suffix = 1, then suffix *= nums[3] = 4)
          result[2] = 2 * 4 = 8 (suffix = 4, then suffix *= nums[2] = 12)
          result[1] = 1 * 12 = 12 (suffix = 12, then suffix *= nums[1] = 24)
          result[0] = 1 * 24 = 24 (suffix = 24)
          Final result = [24, 12, 8, 6] ✓
        """
        n = len(nums)
        result = [1] * n
        
        # First pass: Calculate prefix products (left to right)
        # result[i] = product of all elements before index i
        for i in range(1, n):
            result[i] = result[i - 1] * nums[i - 1]
        
        # Second pass: Multiply by suffix products (right to left)
        # suffix = product of all elements after index i
        suffix = 1
        for i in range(n - 1, -1, -1):
            result[i] *= suffix
            suffix *= nums[i]
        
        return result


# Code - Solution 2: Using Prefix and Suffix Arrays (O(n) space)
class Solution2:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        """
        Product of array except self using separate prefix and suffix arrays.
        
        Approach: 
        1. Calculate prefix products (left to right)
        2. Calculate suffix products (right to left)
        3. Multiply prefix[i] * suffix[i] for each index
        
        Time Complexity: O(n)
        Space Complexity: O(n) - for prefix and suffix arrays
        
        Example: nums = [1,2,3,4]
        prefix = [1, 1, 2, 6]  (product of elements before each index)
        suffix = [24, 12, 4, 1] (product of elements after each index)
        result = [1*24, 1*12, 2*4, 6*1] = [24, 12, 8, 6]
        """
        n = len(nums)
        
        # Calculate prefix products
        prefix = [1] * n
        for i in range(1, n):
            prefix[i] = prefix[i - 1] * nums[i - 1]
        
        # Calculate suffix products
        suffix = [1] * n
        for i in range(n - 2, -1, -1):
            suffix[i] = suffix[i + 1] * nums[i + 1]
        
        # Multiply prefix and suffix
        result = [prefix[i] * suffix[i] for i in range(n)]
        return result


# Code - Solution 3: Brute Force (Not Optimal - O(n²))
class Solution3:
    def productExceptSelf(self, nums: list[int]) -> list[int]:
        """
        Brute force approach - calculate product for each index.
        
        Time Complexity: O(n²) - for each index, multiply all other elements
        Space Complexity: O(1) excluding output array
        
        Not recommended for large inputs.
        """
        n = len(nums)
        result = []
        
        for i in range(n):
            product = 1
            for j in range(n):
                if i != j:
                    product *= nums[j]
            result.append(product)
        
        return result


# Note
# Algorithm: Prefix and Suffix Products
# Key insight: For each index i, we need:
#   answer[i] = (product of all elements before i) × (product of all elements after i)
#
# Optimal Solution (O(1) space):
# 1. Use result array to store prefix products in first pass
# 2. Use a running variable 'suffix' to track suffix products in second pass
# 3. Multiply result[i] by suffix as we go backwards
#
# Why this works:
# - Prefix products: result[i] = nums[0] * nums[1] * ... * nums[i-1]
# - Suffix products: suffix = nums[i+1] * nums[i+2] * ... * nums[n-1]
# - Final: result[i] = prefix[i] * suffix[i]
#
# Example: nums = [1,2,3,4]
# Prefix: [1, 1, 2, 6]
# Suffix: [24, 12, 4, 1]
# Result: [24, 12, 8, 6]
#
# Time Complexity: O(n) - two passes
# Space Complexity: O(1) - only output array (doesn't count) and one variable


# Testcase
def test_productExceptSelf():
    solution = Solution()
    solution2 = Solution2()
    solution3 = Solution3()
    
    # Test case 1
    nums = [1, 2, 3, 4]
    expected = [24, 12, 8, 6]
    assert solution.productExceptSelf(nums) == expected
    assert solution2.productExceptSelf(nums) == expected
    assert solution3.productExceptSelf(nums) == expected
    
    # Test case 2
    nums = [-1, 1, 0, -3, 3]
    expected = [0, 0, 9, 0, 0]
    assert solution.productExceptSelf(nums) == expected
    assert solution2.productExceptSelf(nums) == expected
    assert solution3.productExceptSelf(nums) == expected
    
    # Test case 3: Two elements
    nums = [2, 3]
    expected = [3, 2]
    assert solution.productExceptSelf(nums) == expected
    assert solution2.productExceptSelf(nums) == expected
    assert solution3.productExceptSelf(nums) == expected
    
    # Test case 4: All positive
    nums = [1, 2, 3]
    expected = [6, 3, 2]
    assert solution.productExceptSelf(nums) == expected
    assert solution2.productExceptSelf(nums) == expected
    assert solution3.productExceptSelf(nums) == expected
    
    # Test case 5: With negatives
    nums = [-1, -2, -3]
    expected = [6, 3, 2]
    assert solution.productExceptSelf(nums) == expected
    assert solution2.productExceptSelf(nums) == expected
    assert solution3.productExceptSelf(nums) == expected
    
    # Test case 6: Single zero
    nums = [1, 0, 2]
    expected = [0, 2, 0]
    assert solution.productExceptSelf(nums) == expected
    assert solution2.productExceptSelf(nums) == expected
    assert solution3.productExceptSelf(nums) == expected
    
    # Test case 7: Multiple zeros
    nums = [0, 0, 1]
    expected = [0, 0, 0]
    assert solution.productExceptSelf(nums) == expected
    assert solution2.productExceptSelf(nums) == expected
    assert solution3.productExceptSelf(nums) == expected
    
    print("All test cases passed!")


# Test Result
if __name__ == "__main__":
    test_productExceptSelf()