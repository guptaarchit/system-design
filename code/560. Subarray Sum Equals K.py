# 560. Subarray Sum Equals K
# Medium
# Topics
# conpanies icon
# Companies
# Hint
# Given an array of integers nums and an integer k, return the total number of subarrays whose sum equals to k.

# A subarray is a contiguous non-empty sequence of elements within an array.

 

# Example 1:

# Input: nums = [1,1,1], k = 2
# Output: 2
# Example 2:

# Input: nums = [1,2,3], k = 3
# Output: 2
 

# Constraints:

# 1 <= nums.length <= 2 * 104
# -1000 <= nums[i] <= 1000
# -107 <= k <= 107

from typing import List

class Solution:
    """
    VISUAL EXPLANATION:
    ===================
    
    Array: [1, 2, 3], k = 3
    
    Prefix Sums:
    Index:  0   1   2
    Value:  1   3   6
    Prefix: 1   3   6
    
    We want: prefix[i] - prefix[j] = k
    Which means: sum of subarray from j+1 to i = k
    
    At index 0 (prefix=1):
      Check: 1 - 3 = -2 (not in map, no match)
      Map: {0:1, 1:1}
    
    At index 1 (prefix=3):
      Check: 3 - 3 = 0 (YES! in map with count 1)
      Found subarray [1,2] (indices 0-1) = 3 ✓
      Map: {0:1, 1:1, 3:1}
    
    At index 2 (prefix=6):
      Check: 6 - 3 = 3 (YES! in map with count 1)
      Found subarray [3] (indices 2-2) = 3 ✓
      Map: {0:1, 1:1, 3:1, 6:1}
    
    Result: 2 subarrays
    
    KEY INSIGHT:
    ============
    We're essentially asking: "What prefix sum do I need to subtract
    from my current prefix sum to get k?"
    Answer: current_sum - k
    
    If that value exists in our map, it means we've seen a prefix sum
    that, when subtracted, gives us exactly k. That's our valid subarray!
    """
    def subarraySum(self, nums: List[int], k: int) -> int:
        """
        SIMPLE EXPLANATION:
        ==================
        
        Think of it this way: We're keeping track of running totals (prefix sums) as we go.
        
        KEY IDEA: If the sum from start to position i is X, and the sum from start to 
        position j is (X - k), then the sum from position j+1 to i equals k!
        
        Example: nums = [1, 1, 1], k = 2
        
        Position 0: num = 1
          Running total = 1
          We've seen total 0 before (initialized)
          Check: Do we need (1 - 2) = -1? No, so no match
          Save: total 1 in our map
        
        Position 1: num = 1  
          Running total = 2
          Check: Do we need (2 - 2) = 0? YES! We saw 0 before
          This means: sum from after position -1 (i.e., from start) to position 1 = 2
          Found subarray [1, 1] ✓
          Save: total 2 in our map
        
        Position 2: num = 1
          Running total = 3
          Check: Do we need (3 - 2) = 1? YES! We saw 1 before (at position 0)
          This means: sum from after position 0 to position 2 = 2
          Found subarray [1, 1] ✓
          Save: total 3 in our map
        
        Answer: 2 subarrays
        
        Example 2: nums = [1, 2, 3], k = 3
        
        Position 0: num = 1
          Running total = 1
          Check: Do we need (1 - 3) = -2? No match
          Map: {0: 1, 1: 1}
        
        Position 1: num = 2
          Running total = 3
          Check: Do we need (3 - 3) = 0? YES! We saw 0 before
          This means: sum from start to position 1 = 3
          Found subarray [1, 2] ✓
          Map: {0: 1, 1: 1, 3: 1}
        
        Position 2: num = 3
          Running total = 6
          Check: Do we need (6 - 3) = 3? YES! We saw 3 before (at position 1)
          This means: sum from after position 1 to position 2 = 3
          Found subarray [3] ✓
          Map: {0: 1, 1: 1, 3: 1, 6: 1}
        
        Answer: 2 subarrays ([1,2] and [3])
        
        Example 3: nums = [1, -1, 0], k = 0
        
        Position 0: num = 1
          Running total = 1
          Check: Do we need (1 - 0) = 1? No match yet (we'll see 1 now)
          Map: {0: 1, 1: 1}
        
        Position 1: num = -1
          Running total = 0
          Check: Do we need (0 - 0) = 0? YES! We saw 0 before (initialized)
          Found subarray [1, -1] ✓
          Also, 0 appears again, so Map: {0: 2, 1: 1}
        
        Position 2: num = 0
          Running total = 0
          Check: Do we need (0 - 0) = 0? YES! We saw 0 twice before
          Found subarray [1, -1, 0] ✓ (using first 0)
          Found subarray [0] ✓ (using second 0)
          Map: {0: 3, 1: 1}
        
        Answer: 3 subarrays ([1,-1], [1,-1,0], [0])
        Notice: When same total appears multiple times, we count each occurrence!
        
        WHY {0: 1} INITIALIZATION?
        --------------------------
        We start with {0: 1} to handle subarrays that start from the beginning.
        Without it, we'd miss cases like nums = [2], k = 2
        
        WHY COUNT MULTIPLE TIMES?
        -------------------------
        If we see the same running total multiple times, it means there are multiple
        starting points that create valid subarrays ending at current position.
        """
        # Map: running_total -> how many times we've seen it
        prefix_sum_count = {0: 1}  # Start with 0 seen once
        current_sum = 0
        count = 0
        
        for num in nums:
            # Add current number to running total
            current_sum += num
            
            # Check: Have we seen (current_sum - k) before?
            # If yes, it means there's a subarray ending here that sums to k
            if (current_sum - k) in prefix_sum_count:
                count += prefix_sum_count[current_sum - k]
            
            # Remember this running total for future checks
            prefix_sum_count[current_sum] = prefix_sum_count.get(current_sum, 0) + 1
        
        return count
    
    # Detailed example with negative numbers
    def subarraySum_example_negative(self, nums: List[int], k: int) -> int:
        """
        Example with negative numbers: nums = [1, -1, 1], k = 1
        
        Step 0: prefix_sum_count = {0: 1}, current_sum = 0, count = 0
        
        Step 1: num = 1
        current_sum = 0 + 1 = 1
        Check: (1 - 1) = 0 in map? YES → count += 1  # Found [1] at index 0
        prefix_sum_count = {0: 1, 1: 1}
        
        Step 2: num = -1
        current_sum = 1 + (-1) = 0
        Check: (0 - 1) = -1 in map? No
        prefix_sum_count = {0: 2, 1: 1}  # 0 appears twice now!
        
        Step 3: num = 1
        current_sum = 0 + 1 = 1
        Check: (1 - 1) = 0 in map? YES → count += 2  # Found [1,-1,1] and [1]
        # Why 2? Because 0 appears twice in map:
        #   - [1,-1,1] uses prefix_sum 0 at index 2 minus prefix_sum 0 at index 0
        #   - [1] uses prefix_sum 1 at index 2 minus prefix_sum 0 at index 1
        prefix_sum_count = {0: 2, 1: 2}
        
        Result: 1 + 2 = 3 subarrays: [1], [1,-1,1], [1]
        
        This shows why sliding window fails - we can't shrink when sum > k
        because negative numbers can bring the sum back down to k!
        """
        prefix_sum_count = {0: 1}
        current_sum = 0
        count = 0
        
        for num in nums:
            current_sum += num
            if (current_sum - k) in prefix_sum_count:
                count += prefix_sum_count[current_sum - k]
            prefix_sum_count[current_sum] = prefix_sum_count.get(current_sum, 0) + 1
        
        return count
    
    # Alternative: Brute Force (for understanding) - O(n²)
    def subarraySum_brute_force(self, nums: List[int], k: int) -> int:
        count = 0
        for i in range(len(nums)):
            current_sum = 0
            for j in range(i, len(nums)):
                current_sum += nums[j]
                if current_sum == k:
                    count += 1
        return count
    
    # Alternative: Fixed sliding window (only works for positive numbers)
    def subarraySum_positive_only(self, nums: List[int], k: int) -> int:
        """
        This only works if all numbers are positive.
        Your original approach was trying to do this, but had bugs.
        """
        if not nums:
            return 0
        
        left = 0
        current_sum = 0
        count = 0
        
        for right in range(len(nums)):
            current_sum += nums[right]
            
            # Shrink window while sum > k (only works for positive numbers)
            while current_sum > k and left <= right:
                current_sum -= nums[left]
                left += 1
            
            # Check all possible subarrays ending at 'right' by shrinking from left
            temp_sum = current_sum
            temp_left = left
            
            while temp_left <= right:
                if temp_sum == k:
                    count += 1
                temp_sum -= nums[temp_left]
                temp_left += 1
        
        return count