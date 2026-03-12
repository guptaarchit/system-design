# 215. Kth Largest Element in an Array
# Medium
# Topics
# conpanies icon
# Companies
# Given an integer array nums and an integer k, return the kth largest element in the array.

# Note that it is the kth largest element in the sorted order, not the kth distinct element.

# Can you solve it without sorting?

 

# Example 1:

# Input: nums = [3,2,1,5,6,4], k = 2
# Output: 5
# Example 2:

# Input: nums = [3,2,3,1,2,4,5,5,6], k = 4
# Output: 4
 

# Constraints:

# 1 <= k <= nums.length <= 105
# -104 <= nums[i] <= 104

from typing import List
import heapq

class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        """
        Max-heap (simulated via negation): heapify all, then pop k-1 times.
        kth pop = kth largest. Python heapq is min-heap, so negate for max.
        Time: O(n + k log n), Space: O(n)
        """
        # heap = [-x for x in nums]
        # heapq.heapify(heap)
        # for _ in range(k - 1):
        #     heapq.heappop(heap)
        # return -heapq.heappop(heap)
    
        heap = nums[:k]
        heapq.heapify(heap)
        for x in nums[k:]:
            if x > heap[0]:
                heapq.heapreplace(heap, x)
        return heap[0]