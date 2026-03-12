# 347. Top K Frequent Elements
# Solved
# Medium
# Topics
# conpanies icon
# Companies
# Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.

 

# Example 1:

# Input: nums = [1,1,1,2,2,3], k = 2

# Output: [1,2]

# Example 2:

# Input: nums = [1], k = 1

# Output: [1]

# Example 3:

# Input: nums = [1,2,1,2,1,2,3,1,3,2], k = 2

# Output: [1,2]

 

# Constraints:

# 1 <= nums.length <= 105
# -104 <= nums[i] <= 104
# k is in the range [1, the number of unique elements in the array].
# It is guaranteed that the answer is unique.
 

# Follow up: Your algorithm's time complexity must be better than O(n log n), where n is the array's size.

from typing import List
from collections import Counter
import heapq

class Solution:
    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        """
        Min-heap of size k: keep k most frequent (count, num) pairs.
        Root has smallest count; replace when we see higher count.
        Time: O(n log k), Space: O(n)
        """
        count = Counter(nums)
        # heap = []
        # for num, freq in count.items():
        #     if len(heap) < k:
        #         heapq.heappush(heap, (freq, num))
        #     elif freq > heap[0][0]:
        #         heapq.heapreplace(heap, (freq, num))
        # return [num for _, num in heap]
        count = Counter(nums)
        
        most_common = count.most_common(k)
        
        result = [item[0] for item in most_common]
        
        return result