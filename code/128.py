# 128. Longest Consecutive Sequence
# Medium
# Topics
# conpanies icon
# Companies
# Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence.

# You must write an algorithm that runs in O(n) time.

 

# Example 1:

# Input: nums = [100,4,200,1,3,2]
# Output: 4
# Explanation: The longest consecutive elements sequence is [1, 2, 3, 4]. Therefore its length is 4.
# Example 2:

# Input: nums = [0,3,7,2,5,8,4,6,0,1]
# Output: 9
# Example 3:

# Input: nums = [1,0,1,2]
# Output: 3
 

# Constraints:

# 0 <= nums.length <= 105
# -109 <= nums[i] <= 109
 
# Seen this question in a real interview before?
# 1/5
# Yes
# No
# Accepted
# 3,132,492/6.7M
# Acceptance Rate
# 47.0%

class Solution:
    def longestConsecutive(self, nums: list[int]) -> int:
        """
        Find the length of the longest consecutive sequence.
        Time: O(n) - each number visited at most twice
        Space: O(n) - for the set
        
        Why O(n) despite nested loops?
        ===============================
        Outer loop: iterates through all n numbers in the set
        Inner while loop: only runs when we find the START of a sequence
        
        Key insight: Each number can only be the START of ONE sequence.
        - We only enter the inner loop when (num - 1) is NOT in the set
        - This means num is the smallest number in its sequence
        - When we traverse the sequence [num, num+1, num+2, ...], we visit
          each number in that sequence exactly once
        
        Example: [100, 4, 200, 1, 3, 2]
        - Outer loop checks: 100, 4, 200, 1, 3, 2
        - Only 1, 100, 200 are sequence starts (their num-1 is not in set)
        - For sequence starting at 1: inner loop visits 1, 2, 3, 4 (4 numbers)
        - For sequence starting at 100: inner loop visits 100 (1 number)
        - For sequence starting at 200: inner loop visits 200 (1 number)
        - Total: 6 numbers visited in outer loop + 6 numbers visited in inner loop = 12
        - But we only have 6 unique numbers, so each is visited at most 2 times = O(n)
        """
        if not nums:
            return 0
        
        # Convert to set for O(1) lookup
        num_set = set(nums)
        max_length = 0
        
        # For each number, check if it's the start of a sequence
        for num in num_set:
            # Only process if this is the start of a sequence
            # (i.e., num-1 is not in the set)
            if num - 1 not in num_set:
                # Count consecutive numbers forward
                # This inner loop only runs for sequence starts, and each
                # number in a sequence is visited exactly once here
                current_num = num
                current_length = 1
                
                while current_num + 1 in num_set:
                    current_num += 1
                    current_length += 1
                
                max_length = max(max_length, current_length)
        
        return max_length


# Test cases
if __name__ == "__main__":
    solution = Solution()
    
    # Example 1
    assert solution.longestConsecutive([100, 4, 200, 1, 3, 2]) == 4
    
    # Example 2
    assert solution.longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    
    # Example 3
    assert solution.longestConsecutive([1, 0, 1, 2]) == 3
    
    # Edge case: empty array
    assert solution.longestConsecutive([]) == 0
    
    # Edge case: single element
    assert solution.longestConsecutive([1]) == 1
    
    print("All test cases passed!")