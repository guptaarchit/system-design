# 325. Maximum Size Subarray Sum Equals k
# Medium
# Topics
# Companies
# Hint
# Given an integer array nums and an integer k, return the maximum length of a subarray 
# that sums to k. If there is not one, return 0 instead.

# Example 1:
# Input: nums = [1,-1,5,-2,3], k = 3
# Output: 4
# Explanation: The subarray [1, -1, 5, -2] sums to 3 and is the longest.

# Example 2:
# Input: nums = [-2,-1,2,1], k = 1
# Output: 2
# Explanation: The subarray [-1, 2] sums to 1 and is the longest.

# Constraints:
# 1 <= nums.length <= 2 * 105
# -104 <= nums[i] <= 104
# -109 <= k <= 109


# Code
class Solution:
    def maxSubArrayLen(self, nums: list[int], k: int) -> int:
        """
        Find the maximum length of a subarray that sums to k.
        
        Approach: Prefix Sum + Hash Map
        - Use prefix sums to track cumulative sum up to each index
        - If prefix_sum[i] - prefix_sum[j] = k, then subarray from j+1 to i sums to k
        - Use hash map to store the first occurrence of each prefix sum
        - As we iterate, check if (current_prefix_sum - k) exists in the map
        
        Time Complexity: O(n)
        Space Complexity: O(n)
        
        Detailed Example Walkthrough:
        =============================
        nums = [1, -1, 5, -2, 3], k = 3
        Goal: Find longest subarray summing to 3
        
        Key Insight: If prefix_sum[i] - prefix_sum[j] = k, 
                     then subarray nums[j+1...i] sums to k.
        
        Step-by-step:
        -------------
        Initialize: prefix_sum_map = {0: -1}, prefix_sum = 0, max_len = 0
        (We initialize with {0: -1} to handle subarrays starting at index 0)
        
        i=0, num=1:
          prefix_sum = 0 + 1 = 1
          Check: prefix_sum - k = 1 - 3 = -2
          Is -2 in map? No
          Store: prefix_sum_map[1] = 0
          Map: {0: -1, 1: 0}
          max_len = 0
        
        i=1, num=-1:
          prefix_sum = 1 + (-1) = 0
          Check: prefix_sum - k = 0 - 3 = -3
          Is -3 in map? No
          Store: prefix_sum_map[0] already exists (don't update, keep earliest)
          Map: {0: -1, 1: 0}
          max_len = 0
        
        i=2, num=5:
          prefix_sum = 0 + 5 = 5
          Check: prefix_sum - k = 5 - 3 = 2
          Is 2 in map? No
          Store: prefix_sum_map[5] = 2
          Map: {0: -1, 1: 0, 5: 2}
          max_len = 0
        
        i=3, num=-2:
          prefix_sum = 5 + (-2) = 3
          Check: prefix_sum - k = 3 - 3 = 0
          Is 0 in map? YES! (at index -1)
          Found subarray! Start = -1 + 1 = 0, End = 3
          Subarray: nums[0...3] = [1, -1, 5, -2]
          Sum: 1 + (-1) + 5 + (-2) = 3 ✓
          Length = 3 - (-1) = 4
          max_len = max(0, 4) = 4
          Store: prefix_sum_map[3] = 3
          Map: {0: -1, 1: 0, 5: 2, 3: 3}
        
        i=4, num=3:
          prefix_sum = 3 + 3 = 6
          Check: prefix_sum - k = 6 - 3 = 3
          Is 3 in map? YES! (at index 3)
          Found subarray! Start = 3 + 1 = 4, End = 4
          Subarray: nums[4...4] = [3]
          Sum: 3 ✓
          Length = 4 - 3 = 1
          max_len = max(4, 1) = 4 (keep the longer one)
          Store: prefix_sum_map[6] = 4
          Map: {0: -1, 1: 0, 5: 2, 3: 3, 6: 4}
        
        Result: max_len = 4
        Longest subarray: [1, -1, 5, -2] with length 4
        
        Why initialize with {0: -1}?
        ------------------------------
        Consider nums = [3], k = 3
        Without initialization: prefix_sum = 3, check (3-3=0) not in map → miss the answer
        With initialization: prefix_sum = 3, check (3-3=0) in map at -1 → 
                             subarray from (-1+1)=0 to 0 = [3] ✓
        """
        # Map prefix_sum -> first index where it occurs
        prefix_sum_map = {0: -1}  # Initialize with 0 at index -1 for subarrays starting at index 0
        prefix_sum = 0
        max_len = 0
        
        for i, num in enumerate(nums):
            prefix_sum += num
            
            # Check if we've seen (prefix_sum - k) before
            # If yes, then subarray from (prefix_sum_map[prefix_sum - k] + 1) to i sums to k
            # Why? Because prefix_sum[i] - prefix_sum[j] = k means nums[j+1...i] sums to k
            if prefix_sum - k in prefix_sum_map:
                # Calculate length: from (j+1) to i, inclusive
                # Length = i - (prefix_sum_map[prefix_sum - k] + 1) + 1 = i - prefix_sum_map[prefix_sum - k]
                length = i - prefix_sum_map[prefix_sum - k]
                max_len = max(max_len, length)
            
            # Store the first occurrence of this prefix sum
            # We want the earliest index to maximize the subarray length
            # Only store if we haven't seen this prefix sum before
            if prefix_sum not in prefix_sum_map:
                prefix_sum_map[prefix_sum] = i
        
        return max_len


# Code - Solution 2: Divide and Conquer Approach
class Solution2:
    def maxSubArrayLen(self, nums: list[int], k: int) -> int:
        """
        Find the maximum length of a subarray that sums to k using divide and conquer.
        
        Approach: Divide and Conquer
        - Divide array into left and right halves
        - Recursively find max length in each half
        - Find max length subarray crossing the middle
        - Return maximum of the three
        
        Time Complexity: O(n log n)
        Space Complexity: O(n) for recursion stack and maps
        """
        return self._maxSubArrayLenHelper(nums, 0, len(nums) - 1, k)
    
    def _maxSubArrayLenHelper(self, nums: list[int], left: int, right: int, k: int) -> int:
        # Base case: single element
        if left == right:
            return 1 if nums[left] == k else 0
        
        # Divide
        mid = (left + right) // 2
        
        # Conquer: find max length in left and right halves
        left_max = self._maxSubArrayLenHelper(nums, left, mid, k)
        right_max = self._maxSubArrayLenHelper(nums, mid + 1, right, k)
        
        # Combine: find max length crossing the middle
        cross_max = self._maxCrossingLen(nums, left, mid, right, k)
        
        # Return maximum of the three
        return max(left_max, right_max, cross_max)
    
    def _maxCrossingLen(self, nums: list[int], left: int, mid: int, right: int, k: int) -> int:
        """
        Find maximum length of subarray summing to k that crosses the middle.
        
        Strategy:
        - Build map of suffix sums from left half: suffix_sum -> earliest starting index
        - Build map of prefix sums from right half: prefix_sum -> latest ending index  
        - For each suffix sum s in left, check if (k - s) exists in right prefix sums
        - Calculate length of crossing subarray: end_idx - start_idx + 1
        """
        max_len = 0
        
        # Build suffix sum map for left half (from mid down to left)
        # suffix_sum_map[s] = earliest starting index for suffix sum s
        # We go backwards, but always store the smallest index for each sum
        suffix_sum_map = {}
        suffix_sum = 0
        for i in range(mid, left - 1, -1):
            suffix_sum += nums[i]
            # Store earliest (smallest) index for this suffix sum to maximize length
            # If key exists, update only if current index is smaller
            if suffix_sum not in suffix_sum_map or i < suffix_sum_map[suffix_sum]:
                suffix_sum_map[suffix_sum] = i
        
        # Build prefix sum map for right half (from mid+1 to right)
        # prefix_sum_map[p] = latest ending index for prefix sum p
        # We go forwards and update to ensure we get the latest index for each sum
        prefix_sum_map = {}
        prefix_sum = 0
        for i in range(mid + 1, right + 1):
            prefix_sum += nums[i]
            # Store latest (largest) index for this prefix sum to maximize length
            prefix_sum_map[prefix_sum] = i
        
        # Check for crossing subarrays: suffix_sum_left + prefix_sum_right = k
        for suffix_sum_val, start_idx in suffix_sum_map.items():
            target = k - suffix_sum_val
            if target in prefix_sum_map:
                end_idx = prefix_sum_map[target]
                length = end_idx - start_idx + 1
                max_len = max(max_len, length)
        
        return max_len


# Note
# Algorithm: Prefix Sum + Hash Map
# Key insight: If prefix_sum[i] - prefix_sum[j] = k, then the subarray from j+1 to i sums to k.
#
# Steps:
# 1. Maintain a running prefix sum as we iterate through the array
# 2. For each position, check if (current_prefix_sum - k) exists in our hash map
# 3. If it exists, we found a subarray that sums to k
# 4. Store the first occurrence of each prefix sum to maximize the subarray length
# 5. Initialize map with {0: -1} to handle subarrays starting at index 0
#
# Example walkthrough for nums = [1,-1,5,-2,3], k = 3:
# i=0: prefix_sum=1, check (1-3=-2) not in map, store {0:-1, 1:0}
# i=1: prefix_sum=0, check (0-3=-3) not in map, store {0:-1, 1:0} (0 already exists, don't update)
# i=2: prefix_sum=5, check (5-3=2) not in map, store {0:-1, 1:0, 5:2}
# i=3: prefix_sum=3, check (3-3=0) in map at index -1, length = 3-(-1) = 4, max_len=4
# i=4: prefix_sum=6, check (6-3=3) not in map, store {0:-1, 1:0, 5:2, 3:3, 6:4}
#
# Time Complexity: O(n) - single pass through the array
# Space Complexity: O(n) - hash map can store up to n prefix sums
#
# Algorithm 2: Divide and Conquer
# Key insight: Divide array into halves, recursively solve, then find crossing subarrays.
#
# Steps:
# 1. Divide array into left and right halves
# 2. Recursively find max length in each half
# 3. Find max length subarray crossing the middle:
#    - Build suffix sum map from left half (sum -> earliest start index)
#    - Build prefix sum map from right half (sum -> latest end index)
#    - For each suffix sum s, check if (k - s) exists in prefix sums
#    - Calculate crossing subarray length
# 4. Return maximum of left, right, and crossing results
#
# Time Complexity: O(n log n) - T(n) = 2T(n/2) + O(n)
# Space Complexity: O(n) - recursion stack O(log n) + maps O(n)


# Testcase
def test_maxSubArrayLen():
    solution = Solution()
    solution2 = Solution2()
    
    test_cases = [
        ([1, -1, 5, -2, 3], 3, 4),
        ([-2, -1, 2, 1], 1, 2),
        ([1, 2, 3], 10, 0),
        ([5], 5, 1),
        ([5], 3, 0),
        ([1, 2, 3], 6, 3),
        ([3, 1, 2, 4], 3, 2),
        ([1, 2, 3, 4], 7, 2),
        ([1, 0, -1, 1, 0, -1, 1], 0, 6),
        ([-1, -2, -3, -4], -7, 2),
        ([2, -1, 3, -2, 1], 2, 4),
    ]
    
    for nums, k, expected in test_cases:
        result1 = solution.maxSubArrayLen(nums, k)
        result2 = solution2.maxSubArrayLen(nums, k)
        assert result1 == expected, f"Solution1 failed for {nums}, k={k}: expected {expected}, got {result1}"
        assert result2 == expected, f"Solution2 failed for {nums}, k={k}: expected {expected}, got {result2}"
    
    print("All test cases passed for both solutions!")


# Test Result
if __name__ == "__main__":
    test_maxSubArrayLen()