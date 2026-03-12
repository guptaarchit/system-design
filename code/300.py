# 300. Longest Increasing Subsequence
# Medium
# Topics
# conpanies icon
# Companies
# Given an integer array nums, return the length of the longest strictly increasing subsequence.

 

# Example 1:

# Input: nums = [10,9,2,5,3,7,101,18]
# Output: 4
# Explanation: The longest increasing subsequence is [2,3,7,101], therefore the length is 4.
# Example 2:

# Input: nums = [0,1,0,3,2,3]
# Output: 4
# Example 3:

# Input: nums = [7,7,7,7,7,7,7]
# Output: 1
 

# Constraints:

# 1 <= nums.length <= 2500
# -104 <= nums[i] <= 104
 

# Follow up: Can you come up with an algorithm that runs in O(n log(n)) time complexity?

from typing import List
import bisect

class Solution:
    def lengthOfLIS(self, nums: List[int]) -> int:
        """
        tails[i] = smallest ending element of an increasing subsequence of length i+1.
        For each num: binary search to find/replace. O(n log n).
        """
        tails = []
        for num in nums:
            pos = bisect.bisect_left(tails, num)
            if pos == len(tails):
                tails.append(num)
            else:
                tails[pos] = num
        return len(tails)

    def lengthOfLIS_naive(self, nums: List[int]) -> int:
        """
        Naive DP: dp[i] = length of LIS ending at index i.
        dp[i] = 1 + max(dp[j]) for j < i where nums[j] < nums[i].
        O(n^2) time, O(n) space.
        """
        if not nums:
            return 0
        n = len(nums)
        dp = [1] * n
        for i in range(1, n):
            for j in range(i):
                if nums[j] < nums[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return max(dp)

    def lengthOfLIS_bruteforce(self, nums: List[int]) -> int:
        """
        Brute force: try all subsequences via backtracking.
        At each index: include (if nums[i] > last) or skip.
        O(2^n) time, O(n) recursion stack.
        """
        if not nums:
            return 0

        def dfs(i: int, last: int, length: int) -> None:
            nonlocal best
            if i == len(nums):
                best = max(best, length)
                return
            dfs(i + 1, last, length)  # skip
            if nums[i] > last:
                dfs(i + 1, nums[i], length + 1)  # include

        best = 0
        dfs(0, float('-inf'), 0)
        return best