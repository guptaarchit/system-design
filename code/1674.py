# 1674. Minimum Moves to Make Array Complementary
# Medium
# Topics
# conpanies icon
# Companies
# Hint
# You are given an integer array nums of even length n and an integer limit. In one move, you can replace any integer from nums with another integer between 1 and limit, inclusive.

# The array nums is complementary if for all indices i (0-indexed), nums[i] + nums[n - 1 - i] equals the same number. For example, the array [1,2,3,4] is complementary because for all indices i, nums[i] + nums[n - 1 - i] = 5.

# Return the minimum number of moves required to make nums complementary.

"""
================================================================================
DETAILED EXPLANATION
================================================================================

THE PROBLEM:
-----------
Make all pairs (nums[i], nums[n-1-i]) sum to the SAME target value using 
minimum moves. In one move, you can replace any element with a value between 
1 and limit (inclusive).

KEY INSIGHT - Cost for Each Pair:
---------------------------------
For a pair (a, b) and target sum T:
- 0 moves if T = a + b (already correct!)
- 1 move if we can change ONE element to reach T
  → This happens when T is in range [min(a,b)+1, max(a,b)+limit]
  → Example: (1, 3) with limit=4, target 5: change 1 to 2 → (2, 3) sums to 5
- 2 moves otherwise (must change both elements)

EXAMPLE WALKTHROUGH:
-------------------
Input: nums = [1, 2, 4, 3], limit = 4
Pairs: (1, 3) and (2, 4)

Cost Table:
Target | Pair1 (1,3) | Pair2 (2,4) | Total
-------|-------------|-------------|-------
  2    |   1 move    |   2 moves   |   3
  3    |   1 move    |   1 move    |   2
  4    |   0 moves   |   1 move    |   1  ← Best!
  5    |   1 move    |   1 move    |   2
  6    |   1 move    |   0 moves   |   1  ← Also best!
  7    |   1 move    |   1 move    |   2
  8    |   2 moves   |   1 move    |   3

Answer: 1 move (make both pairs sum to 4 or 6)

HOW THE DIFFERENCE ARRAY WORKS:
------------------------------
Instead of checking each target individually (slow!), we use a "difference array":

1. Start: All targets cost 2 moves (worst case)
2. Mark ranges: Where cost reduces to 1 move
3. Mark points: Where cost reduces to 0 moves  
4. Calculate: Sum up differences to get actual costs

This is like marking "cost changes" on a number line, then walking through to 
calculate the actual cost at each point.

WHY THIS IS EFFICIENT:
---------------------
- Naive approach: O(n × limit) - check each target for each pair
- Difference array: O(n + limit) - mark changes once, then scan once

The difference array technique is perfect when you need to apply the same 
operation to ranges of values!

APPROACH 1 - SIMPLE (Easier to Understand):
-------------------------------------------
1. Try every possible target sum from 2 to 2*limit
2. For each target, calculate cost for each pair:
   - If pair already sums to target: 0 moves
   - If we can change one element: 1 move
   - Otherwise: 2 moves
3. Sum up costs for all pairs at each target
4. Return the minimum total cost

Time: O(n × limit) - straightforward but a bit slower
This is the approach used in minMoves() - much easier to understand!

APPROACH 2 - OPTIMIZED (Using Difference Array):
-----------------------------------------------
1. Use difference array to mark cost changes efficiently
2. Process all pairs once, marking where costs change
3. Scan through targets once to calculate actual costs
4. Return minimum

Time: O(n + limit) - faster but harder to understand
This is the approach used in minMoves_optimized()
"""

 

# Example 1:

# Input: nums = [1,2,4,3], limit = 4
# Output: 1
# Explanation: In 1 move, you can change nums to [1,2,2,3] (underlined elements are changed).
# nums[0] + nums[3] = 1 + 3 = 4.
# nums[1] + nums[2] = 2 + 2 = 4.
# nums[2] + nums[1] = 2 + 2 = 4.
# nums[3] + nums[0] = 3 + 1 = 4.
# Therefore, nums[i] + nums[n-1-i] = 4 for every i, so nums is complementary.
# Example 2:

# Input: nums = [1,2,2,1], limit = 2
# Output: 2
# Explanation: In 2 moves, you can change nums to [2,2,2,2]. You cannot change any number to 3 since 3 > limit.
# Example 3:

# Input: nums = [1,2,1,2], limit = 2
# Output: 0
# Explanation: nums is already complementary.
 

# Constraints:

# n == nums.length
# 2 <= n <= 105
# 1 <= nums[i] <= limit <= 105
# n is even.

class Solution:
    def minMoves(self, nums: list[int], limit: int) -> int:
        """
        SIMPLE APPROACH (Easier to Understand):
        Try every possible target sum from 2 to 2*limit.
        For each target, calculate the total cost to make all pairs sum to that target.
        Return the minimum cost.
        
        Time: O(n * limit) where n is array length
        Space: O(1)
        """
        n = len(nums)
        min_moves = float('inf')
        
        # Try every possible target sum
        # WHY range(2, 2*limit + 1)?
        # 
        # From constraints: 1 <= nums[i] <= limit
        # A pair is (a, b) where both a and b are in [1, limit]
        # 
        # Minimum possible sum: min(a) + min(b) = 1 + 1 = 2
        # Maximum possible sum: max(a) + max(b) = limit + limit = 2 * limit
        # 
        # So valid target sums are: 2, 3, 4, ..., 2*limit
        # 
        # Example with limit=4:
        #   - Minimum pair: (1, 1) → sum = 2
        #   - Maximum pair: (4, 4) → sum = 8
        #   - Check targets: 2, 3, 4, 5, 6, 7, 8
        # 
        # range(2, 2*limit + 1) gives us [2, 3, 4, ..., 2*limit]
        for target in range(2, 2 * limit + 1):
            total_cost = 0
            
            # Calculate cost for each pair to reach this target
            for i in range(n // 2):
                a, b = nums[i], nums[n - 1 - i]
                
                if a + b == target:
                    # Already correct - 0 moves needed
                    cost = 0
                elif min(a, b) + 1 <= target <= max(a, b) + limit:
                    # Can change one element to reach target - 1 move
                    # Example: (1, 3), target=5: change 1 to 2 → (2, 3) sums to 5
                    cost = 1
                else:
                    # Need to change both elements - 2 moves
                    cost = 2
                
                total_cost += cost
            
            min_moves = min(min_moves, total_cost)
        
        return min_moves
    
    def minMoves_optimized(self, nums: list[int], limit: int) -> int:
        """
        OPTIMIZED APPROACH (Using Difference Array):
        More efficient but harder to understand.
        Uses difference array to track cost changes efficiently.
        
        Time: O(n + limit)
        Space: O(limit)
        """
        n = len(nums)
        # Possible target sums range from 2 (1+1) to 2*limit (limit+limit)
        # diff[i] = how much the cost changes at target sum i
        diff = [0] * (2 * limit + 2)
        
        # Process each pair
        for i in range(n // 2):
            a, b = nums[i], nums[n - 1 - i]
            min_val = min(a, b)
            max_val = max(a, b)
            
            # STEP 1: Start with base cost of 2 moves for ALL targets
            diff[2] += 2
            diff[2 * limit + 1] -= 2  # Reset after the last valid target
            
            # STEP 2: Targets in range [min_val+1, max_val+limit] cost 1 move
            # This is where we can change one element to reach the target
            # We reduce cost by 1 (from 2 to 1) in this range
            diff[min_val + 1] -= 1  # Start reducing at min_val+1
            diff[max_val + limit + 1] += 1  # Stop reducing after max_val+limit
            
            # STEP 3: Target = a+b costs 0 moves (reduce cost by 1 more)
            # If a+b is in the range above, it's already at cost 1, so -1 → 0
            # If a+b is NOT in the range, it's at cost 2, so we need -2 total
            if min_val + 1 <= a + b <= max_val + limit:
                # a+b is in range, already reduced to 1, reduce by 1 more → 0
                diff[a + b] -= 1
                diff[a + b + 1] += 1
            else:
                # a+b is not in range, still at cost 2, reduce by 2 → 0
                diff[a + b] -= 2
                diff[a + b + 1] += 2
        
        # Now calculate actual costs by summing up the differences
        # This is like: cost[target] = sum of all diff[i] where i <= target
        min_moves = float('inf')
        cost = 0
        
        for target in range(2, 2 * limit + 1):
            cost += diff[target]  # Accumulate changes
            min_moves = min(min_moves, cost)  # Track minimum
        
        return min_moves


def explain_example(nums, limit):
    """
    Detailed walkthrough of how the algorithm works.
    """
    print(f"\n=== EXPLANATION: nums = {nums}, limit = {limit} ===")
    n = len(nums)
    pairs = []
    for i in range(n // 2):
        pairs.append((nums[i], nums[n - 1 - i]))
    print(f"Pairs: {pairs}")
    
    print("\nFor each pair, let's see the cost for different target sums:")
    for idx, (a, b) in enumerate(pairs):
        print(f"\nPair {idx+1}: ({a}, {b})")
        print(f"  Current sum: {a + b}")
        print(f"  Cost for different targets:")
        
        for target in range(2, 2 * limit + 1):
            if target == a + b:
                cost = 0
                reason = "Already correct (0 moves)"
            elif min(a, b) + 1 <= target <= max(a, b) + limit:
                cost = 1
                reason = "Can change one element (1 move)"
            else:
                cost = 2
                reason = "Need to change both (2 moves)"
            
            if target <= 10:  # Only show first few for clarity
                print(f"    Target {target}: {cost} moves - {reason}")
    
    print("\nNow we find the target that minimizes total cost across all pairs:")
    print("(This is what the difference array efficiently calculates)")


# Test cases
if __name__ == "__main__":
    # Show explanation for Example 1
    explain_example([1, 2, 4, 3], 4)
    
    sol = Solution()
    
    test_cases = [
        ([1, 2, 4, 3], 4, 1),
        ([1, 2, 2, 1], 2, 2),
        ([1, 2, 1, 2], 2, 0),
    ]
    
    print("\n" + "="*60)
    print("Testing SIMPLE approach (easier to understand):")
    print("="*60)
    
    for nums, limit, expected in test_cases:
        result = sol.minMoves(nums, limit)
        print(f"nums={nums}, limit={limit} → {result} moves (expected {expected})")
        assert result == expected, f"Failed! Got {result}, expected {expected}"
    
    print("\n" + "="*60)
    print("Testing OPTIMIZED approach (both should give same results):")
    print("="*60)
    
    for nums, limit, expected in test_cases:
        result_simple = sol.minMoves(nums, limit)
        result_optimized = sol.minMoves_optimized(nums, limit)
        print(f"nums={nums}, limit={limit}")
        print(f"  Simple: {result_simple} moves")
        print(f"  Optimized: {result_optimized} moves")
        assert result_simple == result_optimized == expected
    
    print("\n✅ All test cases passed!")
    print("\n💡 TIP: Use minMoves() for easier understanding, minMoves_optimized() for better performance!")