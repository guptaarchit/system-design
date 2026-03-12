# Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

# You may assume that each input would have exactly one solution, and you may not use the same element twice.

# You can return the answer in any order.

 

# Example 1:

# Input: nums = [2,7,11,15], target = 9
# Output: [0,1]
# Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
# Example 2:

# Input: nums = [3,2,4], target = 6
# Output: [1,2]
# Example 3:

# Input: nums = [3,3], target = 6
# Output: [0,1]
 

# Constraints:

# 2 <= nums.length <= 104
# -109 <= nums[i] <= 109
# -109 <= target <= 109
# Only one valid answer exists.
 

# Follow-up: Can you come up with an algorithm that is less than O(n2) time complexity?


def two_sum(nums, target):
    """
    Optimized solution using hash map (frequency map pattern).
    
    Time Complexity: O(n) - single pass through array
        - Loop through array: O(n)
        - Dictionary lookup (complement in num_map): O(1) average case
        - Dictionary insertion (num_map[num] = i): O(1) average case
        - Overall: O(n) * O(1) = O(n)
    
    Space Complexity: O(n) - hash map stores at most n elements
    
    Approach:
    - Use a hash map to store {number: index} pairs
    - For each number, check if complement (target - num) exists in map
    - If found, return indices; otherwise add current number to map
    
    Note: Dictionary operations (lookup, insertion) are O(1) average case
    due to hash table implementation. Worst case O(n) only with hash collisions.
    """
    num_map = {}  # {number: index}
    
    for i, num in enumerate(nums):
        complement = target - num
        
        # Check if complement exists in map
        # Time Complexity: O(1) average case, O(n) worst case (rare hash collisions)
        # Dictionary lookup in Python uses hash table - average O(1) constant time
        if complement in num_map:
            return [num_map[complement], i]
        
        # Store current number and its index
        num_map[num] = i
    
    return []  # Should never reach here per problem constraints


# Test cases
if __name__ == "__main__":
    # Example 1
    nums1 = [2, 7, 11, 15]
    target1 = 9
    print(f"Input: nums = {nums1}, target = {target1}")
    print(f"Output: {two_sum(nums1, target1)}")  # Expected: [0, 1]
    print()
    
    # Example 2
    nums2 = [3, 2, 4]
    target2 = 6
    print(f"Input: nums = {nums2}, target = {target2}")
    print(f"Output: {two_sum(nums2, target2)}")  # Expected: [1, 2]
    print()
    
    # Example 3
    nums3 = [3, 3]
    target3 = 6
    print(f"Input: nums = {nums3}, target = {target3}")
    print(f"Output: {two_sum(nums3, target3)}")  # Expected: [0, 1]